import argparse

parser = argparse.ArgumentParser(prog='PROG')
subparsers = parser.add_subparsers(help='sub-command help')

parser_pm=subparsers.add_parser("pm",help="包管理器")
subparsers_pm=parser_pm.add_subparsers(help='sub-command help')
parser_pm_install=subparsers_pm.add_parser("install",help="安装")
parser_pm_list=subparsers_pm.add_parser("list",help="列出已安装音源")

args = parser.parse_args()

