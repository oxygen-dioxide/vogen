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
	
	#设置
	def config(args):#输出当前设置
		from vogen import config
		from tabulate import tabulate
		print(tabulate(config.config.items(),headers=["Key","Value"]))
	parser_config=subparsers.add_parser("config",help="设置")
	parser_config.set_defaults(func=config)
	subparsers_config=parser_config.add_subparsers(help='')
	#修改设置
	def config_set(args):
		from vogen import config
		config.set(args.key,args.value)
	parser_config_set=subparsers_config.add_parser("set",help="修改设置")
	parser_config_set.set_defaults(func=config_set)
	parser_config_set.add_argument('key',type=str)
	parser_config_set.add_argument('value',type=str)

	#合成
	def synth(args):
		import os
		import wavio
		from vogen import synth
		from vogen.synth import utils
		infile=args.infile
		if(args.outfile==""):
			outfile=infile[:-4]+".wav"
		else:
			outfile=args.outfile
		#如果输出文件已存在
		if(os.path.isfile(outfile)):
			print(outfile+" 已存在，是否覆盖？\ny:覆盖并合成  n:保留并放弃合成")
			instr=input()
			while(len(instr)==0 or not(instr[0] in ("y","n","Y","N"))):
				print("y:覆盖并合成 n:保留并放弃合成")
				instr=input()
			if(instr[0] in ("n","N")):
				return
		wavio.write(outfile,synth.synth(vogen.openvog(infile,False)),utils.Params.fs)
		
	parser_synth=subparsers.add_parser("synth",help="合成")
	parser_synth.set_defaults(func=synth)
	parser_synth.add_argument("infile",type=str,help="输入文件")
	parser_synth.add_argument("outfile",type=str,nargs='?',default="",help="输出文件")
	parser_synth.add_argument("-F,--force",action="store_true",help="强制覆盖现有文件")

	args = parser.parse_args()
	#print(args)
	args.func(args)

if(__name__=="__main__"):
	main()