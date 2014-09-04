#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import datetime
import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from sortinghat import api
from sortinghat.cmd.show import Show
from sortinghat.db.database import Database

from tests.config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT


SHOW_UUID_NOT_FOUND_ERROR = "Error: FFFFFFFFFFFFFFF not found in the registry"

SHOW_EMPTY_OUTPUT = ""

SHOW_OUTPUT = """unique identity 0000000000000000000000000000000000000000

No identities

No enrollments


unique identity 03e12d00e37fd45593c49a5a5a1652deca4cf302

Identities:
  John Smith\tjsmith@example.com\tjsmith\tscm
  John Smith\tjsmith@example.com\t-\tscm

Enrollments:
  Example\t1900-01-01 00:00:00\t2100-01-01 00:00:00


unique identity 52e0aa0a14826627e633fd15332988686b730ab3

Identities:
  Jane Roe\tjroe@example.com\tjroe\tscm
  -\tjroe@bitergia.com\t-\tunknown
  -\tjroe@example.com\t-\tscm

Enrollments:
  Bitergia\t1999-01-01 00:00:00\t2000-01-01 00:00:00
  Bitergia\t2006-01-01 00:00:00\t2008-01-01 00:00:00
  Example\t1900-01-01 00:00:00\t2100-01-01 00:00:00"""

SHOW_UUID_OUTPUT = """unique identity 52e0aa0a14826627e633fd15332988686b730ab3

Identities:
  Jane Roe\tjroe@example.com\tjroe\tscm
  -\tjroe@bitergia.com\t-\tunknown
  -\tjroe@example.com\t-\tscm

Enrollments:
  Bitergia\t1999-01-01 00:00:00\t2000-01-01 00:00:00
  Bitergia\t2006-01-01 00:00:00\t2008-01-01 00:00:00
  Example\t1900-01-01 00:00:00\t2100-01-01 00:00:00"""


class TestBaseCase(unittest.TestCase):
    """Defines common setup and teardown methods on show unit tests"""

    def setUp(self):
        if not hasattr(sys.stdout, 'getvalue'):
            self.fail('This test needs to be run in buffered mode')

        # Create a connection to check the contents of the registry
        self.db = Database(DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT)

        # Import predefined dataset for testing
        self._load_test_dataset()

        # Create command
        self.kwargs = {'user' : DB_USER,
                       'password' : DB_PASSWORD,
                       'database' :DB_NAME,
                       'host' : DB_HOST,
                       'port' : DB_PORT}
        self.cmd = Show(**self.kwargs)

    def tearDown(self):
        self.db.clear()

    def _load_test_dataset(self):
        # Add organizations
        api.add_organization(self.db, 'Example')
        api.add_organization(self.db, 'Bitergia')

        # Add John Smith identity
        jsmith_uuid = api.add_identity(self.db, 'scm', 'jsmith@example.com',
                                       'John Smith', 'jsmith')
        api.add_identity(self.db, 'scm', 'jsmith@example.com', 'John Smith',
                         uuid=jsmith_uuid)

        # Add Joe Roe identity
        jroe_uuid = api.add_identity(self.db, 'scm', 'jroe@example.com',
                                     'Jane Roe', 'jroe')
        api.add_identity(self.db, 'scm', 'jroe@example.com',
                         uuid=jroe_uuid)
        api.add_identity(self.db, 'unknown', 'jroe@bitergia.com',
                         uuid=jroe_uuid)

        # Add unique identity, this one won't have neither identities
        # nor enrollments 
        api.add_unique_identity(self.db,
                                '0000000000000000000000000000000000000000')

        # Add enrollments
        api.add_enrollment(self.db, jsmith_uuid, 'Example')

        api.add_enrollment(self.db, jroe_uuid, 'Example')
        api.add_enrollment(self.db, jroe_uuid, 'Bitergia',
                           datetime.datetime(1999, 1, 1),
                           datetime.datetime(2000, 1, 1))
        api.add_enrollment(self.db, jroe_uuid, 'Bitergia',
                           datetime.datetime(2006, 1, 1),
                           datetime.datetime(2008, 1, 1))

class TestShowCommand(TestBaseCase):
    """Unit tests for show command"""

    def test_show(self):
        """Check show output"""

        self.cmd.run()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, SHOW_OUTPUT)

    def test_log_uuid(self):
        """Check log using a uuid"""

        self.cmd.run('52e0aa0a14826627e633fd15332988686b730ab3')
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, SHOW_UUID_OUTPUT)

    def test_empty_registry(self):
        """Check output when the registry is empty"""

        # Delete the contents of the database
        self.db.clear()

        self.cmd.run()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, SHOW_EMPTY_OUTPUT)


class TestShow(TestBaseCase):
    """Unit tests for show"""

    def test_show(self):
        "Check show"

        self.cmd.show()
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, SHOW_OUTPUT)

    def test_show_uuid(self):
        """Check show using a uuid"""

        self.cmd.show('52e0aa0a14826627e633fd15332988686b730ab3')
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, SHOW_UUID_OUTPUT)

    def test_not_found_uuid(self):
        """Check whether it raises an error when the uiid is not available"""

        self.cmd.show('FFFFFFFFFFFFFFF')
        output = sys.stderr.getvalue().strip()
        self.assertEqual(output, SHOW_UUID_NOT_FOUND_ERROR)

    def test_empty_registry(self):
        """Check output when the registry is empty"""

        # Delete the contents of the database
        self.db.clear()

        self.cmd.show()
        output = sys.stderr.getvalue().strip()
        self.assertEqual(output, SHOW_EMPTY_OUTPUT)


if __name__ == "__main__":
    unittest.main(buffer=True, exit=False)
