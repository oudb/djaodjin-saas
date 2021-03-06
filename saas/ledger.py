# Copyright (c) 2013, Fortylines LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime, logging
from django.db import connection
from saas.models import Organization

LOGGER = logging.getLogger(__name__)

def balance(organization):
    """returns balance due for an organization"""
    if isinstance(organization, basestring):
        try:
            organization = Organization.objects.get(name=organization)
        except Organization.DoesNotExist:
            raise
    balances = read_balances()
    if organization.name in balances:
        return balances[organization.name]
    return 0


def read_balances(until=datetime.datetime.now()):
    """Balances associated to customer accounts.

    We are executing the following SQL to find the balance
    of each customer.

    The query returns a list of tuples (organization_id, amount in cents)
    we use to create the invoices.
    example:
        (2, 1200)
        (3, 1100)

    """
    account = 'Balance'
    cursor = connection.cursor()
    cursor.execute(
"""select t1.dest_organization_id, sum(t1.amount - coalesce(t2.amount, 0))
from saas_transaction t1 left outer join saas_transaction t2
on t1.dest_organization_id = t2.orig_organization_id
   and t1.dest_account = t2.orig_account
where t1.dest_account = '%s'
group by t1.dest_organization_id
""" % account)
    return cursor.fetchall()
