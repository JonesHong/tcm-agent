# -*- coding: utf-8 -*-
import argparse
import os
import sys

import redis


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
    def set_redis_client(self,redis_client):
        self.agent.redis_client = redis_client
    
def argparse_handler():
    def str_to_bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'y'):
            return True
        elif v.lower() in ('no', 'n'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--redis_port', '-rp', type=int, default=51201, help="Websocket port to run the server on.")
    parser.add_argument('--redis_host','-rh', type=str, default="localhost", help="Websocket host to run the server on.")
    global args
    args = parser.parse_args()

# agent = AgentService.agent
# agent.sex = 'female'
# agent.invoke('')
if __name__ == '__main__':
    
    argparse_handler()
    global redis_client
    redis_client = redis.Redis(host=args.redis_host, port=args.redis_port)
    agent_service = AgentService()
    agent_service.set_redis_client(redis_client)
    agent_service.cmdloop()
