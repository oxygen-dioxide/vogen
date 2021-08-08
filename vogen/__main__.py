import vogen
import argparse
from typing import List
	
def main():
	#显示默认帮助
	def pyvogen_default(args):
		print("PyVogen命令行工具\n\npm 包管理器\nversion 显示版本信息\n\n可在此找到更多帮助：https://gitee.com/oxygendioxide/vogen")
	parser = argparse.ArgumentParser(prog='pyvogen')
	parser.set_defaults(func=pyvogen_default)
	subparsers = parser.add_subparsers(help='sub-command help')
	
	#显示版本信息
	def showversion(args):
		import sys
		import onnxruntime
		print("pyvogen version: {}".format(vogen.__version__))
		print("onnxruntime version: {}".format(onnxruntime.__version__))
		print("python version: {}".format(sys.version))
	parser_version=subparsers.add_parser("version",help="显示版本信息")
	parser_version.set_defaults(func=showversion)
	
	#包管理器
	parser_pm=subparsers.add_parser("pm",help="包管理器")
	subparsers_pm=parser_pm.add_subparsers(help='')
	#安装
	def pm_install(args):
		from vogen import pm
		install_func=pm.install
		if(args.local):
			install_func=pm.install_local
		elif(args.online):
			install_func=pm.install_online
		for i in args.name:
			install_func(i,force=args.force)
	parser_pm_install=subparsers_pm.add_parser("install",help="安装")
	parser_pm_install.add_argument('name',type=str,nargs='+')
	parser_pm_install.add_argument('-l',"--local",action='store_true',help='从本地包安装')
	parser_pm_install.add_argument('-o',"--online",action='store_true',help="下载在线包并安装")
	parser_pm_install.add_argument('-F',"--force",action='store_true',help="强制覆盖现有文件")
	parser_pm_install.set_defaults(func=pm_install)
	#列出已安装音源
	def pm_list(args):
		from vogen import pm
		print("\n".join(pm.list()))
	parser_pm_list=subparsers_pm.add_parser("list",help="列出已安装音源")
	parser_pm_list.set_defaults(func=pm_list)
	#卸载
	def pm_uninstall(args):
		from vogen import pm
		pm.uninstall(args.id)
	parser_pm_uninstall=subparsers_pm.add_parser("uninstall",help="卸载")
	parser_pm_uninstall.add_argument("id")
	parser_pm_uninstall.set_defaults(func=pm_uninstall)
	
	args = parser.parse_args()
	print(args)
	args.func(args)

if(__name__=="__main__"):
	main()