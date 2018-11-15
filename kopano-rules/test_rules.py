import kopano_rules
import unittest
import kopano



class RulesTest(unittest.TestCase):
    """
        Test the createrule function
    """

    def _conditions(self):
        return [
            {'received-from': 'user2@farmer.lan'},
            {'name-in-cc': None},
            {'name-in-to': None},
            {'name-in-to-cc': None},
            {'sent-to': 'user2@farmer.lan'},
            {'importance': 'high'},
            {'sensitivity': 'private'},
            {'sent-only-to-me': None},
            {'contain-word-in-body': 'hello'},
            {'contain-word-in-header': 'hello'},
            {'contain-word-in-subject': 'hello'},
            {'contain-word-sender-address': 'hello'},
            {'contain-word-recipient-address': 'hello'},
            {'message-size': '666,777'},
            {'received-date': '04-01-1990,04-02-1990'},
            {'has-attachment': None},
        ]

    def _actions(self):
        return [
            {'forward-to':  'user2@farmer.lan'},
            {'redirect-to': 'user2@farmer.lan'},
            {'forward-as-attachment': 'user2@farmer.lan'},
            {'move-to': 'inbox'},
            {'copy-to': 'inbox'},
            {'delete':  None},
            {'mark-as-read': None},
            {'mark-as-junk':  None},
            # {'mark-as-importance': 'high'} ## broken
        ]
    def _printing(self, text):
        totalhash = len(text) + 2
        comment = ''
        for a in range(totalhash):
            comment += '#'
        comment += '\n# {}\n{}'.format(text,comment)
        print(comment)
    def setUp(self):
        self._printing('Clear rules')
        self.server = kopano.Server(auth_user='admin', auth_pass='admin')
        kopano_rules.kopano_rule( self.server, 'user1', emptyRules=True)


    def test_list_rules_empty(self):
        self._printing('Test print empty rules list')
        with self.assertRaises(SystemExit) as cm:
            kopano_rules.kopano_rule(self.server, 'user1', listrules=True)
        self.assertEqual(cm.exception.code, 0)

    def test_create_rule_actions(self):
        self._printing('Test Create action rules')
        num=1
        ## Grep the first conditions
        condition = self._conditions()[0]
        name = list(condition.keys())[0]
        value = condition[name]
        condition_list = []
        if value:
            condition_list.append("{}:{}".format(name, value))
        else:
            condition_list.append(name)

        for action in self._actions():
            # if action:
            name = list(action.keys())[0]
            value = action[name]
            action_list = []
            if value:
                action_list.append("{}:{}".format(name, value))
            else:
                action_list.append(name)

            with self.assertRaises(SystemExit) as cm:

                kopano_rules.kopano_rule(self.server, 'user1', rulename=name, actions=action_list,
                                         conditions=condition_list)

            self.assertEqual(cm.exception.code, 0)
            num += 1

        with self.assertRaises(SystemExit) as cm:
            kopano_rules.kopano_rule(self.server, 'user1', listrules=True)
        self.assertEqual(cm.exception.code, 0)

    def test_create_rule_conditions(self):
        self._printing('Test Create conditions rules ')
        num = 1
        ## Grep the first action
        action = self._actions()[0]
        name = list(action.keys())[0]
        value = action[name]
        action_list = []
        if value:
            action_list.append("{}:{}".format(name, value))
        else:
            action_list.append(name)

        for condition in self._conditions():
            # if action:
            name = list(condition.keys())[0]
            value = condition[name]
            condition_list = []
            if value:
                condition_list.append("{}:{}".format(name, value))
            else:
                condition_list.append(name)

            with self.assertRaises(SystemExit) as cm:

                kopano_rules.kopano_rule(self.server, 'user1', rulename=name, actions=action_list,
                                         conditions=condition_list)
            self.assertEqual(cm.exception.code, 0)
            num += 1

        with self.assertRaises(SystemExit) as cm:
            kopano_rules.kopano_rule(self.server, 'user1', listrules=True)
        self.assertEqual(cm.exception.code, 0)


    def test_disable_rule(self):
        self._printing('Test disable rules')
        action = self._actions()[0]
        name = list(action.keys())[0]
        value = action[name]
        action_list = []
        if value:
            action_list.append("{}:{}".format(name, value))
        else:
            action_list.append(name)

        condition = self._conditions()[0]
        name = list(condition.keys())[0]
        value = condition[name]
        condition_list = []
        if value:
            condition_list.append("{}:{}".format(name, value))
        else:
            condition_list.append(name)

        with self.assertRaises(SystemExit) as cm:
            kopano_rules.kopano_rule(self.server, 'user1', rulename=name, actions=action_list,
                                     conditions=condition_list)
        self.assertEqual(cm.exception.code, 0)

        with self.assertRaises(SystemExit) as cm:
            kopano_rules.kopano_rule(self.server, 'user1', rule=1, state='disable')
        self.assertEqual(cm.exception.code, 0)

    def test_delete_rule(self):
        self._printing('Test delete rules')
        action = self._actions()[0]
        name = list(action.keys())[0]
        value = action[name]
        action_list = []
        if value:
            action_list.append("{}:{}".format(name, value))
        else:
            action_list.append(name)

        condition = self._conditions()[0]
        name = list(condition.keys())[0]
        value = condition[name]
        condition_list = []
        if value:
            condition_list.append("{}:{}".format(name, value))
        else:
            condition_list.append(name)

        with self.assertRaises(SystemExit) as cm:
            kopano_rules.kopano_rule(self.server, 'user1', rulename=name, actions=action_list,
                                     conditions=condition_list)
        self.assertEqual(cm.exception.code, 0)

        with self.assertRaises(SystemExit) as cm:
            kopano_rules.kopano_rule(self.server, 'user1', rule=1, state='delete')
        self.assertEqual(cm.exception.code, 0)
if __name__ == '__main__':
    unittest.main()