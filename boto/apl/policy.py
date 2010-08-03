# Copyright (c) 2006-2009 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import simplejson
import uuid

class Principal(dict):

    def __setitem__(self, key, value):
        if self.has_key(key):
            current_value = self[key]
            if isinstance(current_value, list):
                current_value.append(value)
                return
            else:
                value = [current_value, value]
        dict.__setitem__(self, key, value)

class ConditionBlock(dict):
    """
    A condition block.  The various conditions are defined below.
    The following Keys are available across all services:
    
    * AWS:CurrentTime
    * AWS:SecureTransport
    * AWS:SourceIp
    * AWS:UserAgent

    """

    Keys = ['AWS:CurrentTime',
            'AWS:SecureTransport',
            'AWS:SourceIp',
            'AWS:UserAgent']

    StringConditions = ['StringEquals',
                        'StringNotEquals',
                        'StringEqualsIgnoreCase',
                        'StringNotEqualsIgnoreCase',
                        'StringLike',
                        'StringNotLike']

    NumericConditions = ['NumericEquals',
                         'NumericNotEquals',
                         'NumericLessThan',
                         'NumericLessThanEquals',
                         'NumericGreaterThan',
                         'NumericGreaterThanEquals']

    DateConditions = ['DateEquals',
                      'DateNotEquals',
                      'DateLessThan',
                      'DateLessThanEquals',
                      'DateGreaterThan',
                      'DateGreaterThanEquals']

    BooleanConditions = ['Bool']

    IpAddressConditions = ['IpAddress',
                           'NotIpAddress']
class Statement(dict):

    Actions = []

    def __init__(self, id):
        self['Sid'] = id
        self['Principal'] = Principal()
        self['Action'] = None

    def _set_effect(self, effect):
        legal_values = ['Allow', 'Deny']
        if effect not in legal_values:
            raise ValueError, 'Effect must be one of %s' % legal_values
        self['Effect'] = effect

    def _get_effect(self):
        if self.has_key('Effect'):
            return self['Effect']
        else:
            return None

    effect = property(_get_effect, _set_effect, None,
                      'The Effect for this Statement')

    def _set_resource(self, resource):
        self['Resource'] = resource

    def _get_resource(self):
        if self.has_key('Resource'):
            return self['Resource']
        else:
            return None

    resource = property(_get_resource, _set_resource, None,
                      'The resource for this Statement')

    def _set_action(self, action):
        if action not in self.Actions:
            raise ValueError, 'Action must be one of %s' % self.Actions
        self['Action'] = action

    def _get_action(self):
        return self['Action']

    action = property(_get_action, _set_action, None,
                      'The action for this Statement')

    def add_condition(self, key, operator, values):
        if key not in self.Keys:
            raise ValueError, 'key must be one of %s' % self.Keys

class SQSStatement(Statement):

    Actions = ['SQS:SendMessge', 'SQS:ReceiveMessage', 'SQS:*']
    
class Policy(dict):

    def __init__(self, version='2008-10-17'):
        self.statement_cls = Statement
        self._sid_cnt = 1
        self['Version'] = version
        self['Id'] = str(uuid.uuid4())
        self['Statement'] = []

    def __getattr__(self, name):
        return self[name.capitalize()]

    def new_statement(self):
        s = self.statement_cls(str(self._sid_cnt))
        self._sid_cnt += 1
        self['Statement'].append(s)
        return s

    def to_json(self):
        return simplejson.dumps(self)

class SQSPolicy(Policy):

    def __init__(self, version='2008-10-17'):
        Policy.__init__(self, version)
        self.statement_cls = SQSStatement
        

    
