# -*- coding: utf-8 -*-
import os
import sys


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 添加项目根目录到 sys.path
sys.path.append(project_root)
import json
import cmd

from util.agent.core import Agent


# InteractiveAgent
class AgentService(cmd.Cmd):
    intro = 'Welcome to the interactive agent. Type help or ? to list commands.\n'
    prompt = '(user) '
    agent = Agent()

    def default(self, line):
        response = self.agent.invoke(line)
        print(f"(agent) {response}")

    def do_exit(self, line):
        """Exit the interactive agent."""
        print('Exiting the interactive agent.')
        return True

# agent = AgentService.agent
# agent.sex = 'female'
# agent.invoke('')
if __name__ == '__main__':
    AgentService().cmdloop()
