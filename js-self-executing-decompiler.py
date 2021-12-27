#!/usr/bin/pypy
# -*- coding:utf-8 -*-
import re,sys,os,argparse,pathlib
from py_mini_racer import py_mini_racer
VERSION = '0.01'
JS_BUILTIN_FUNCTIONS='split'

def main(path,isHexadecimal=False):
	with open (path,'r+',encoding='utf-8') as file:
		
		isArray=False 
		if not isHexadecimal:
			content=file.readlines()
			first=1 if '/*' in content[0] else 0
			for i in range(first,5): 
				first_line=content[i]
				args=re.search(re.compile(r'(?<=function\().*?(?=\)\s?\{)'),first_line)[0].split(',')
				if args:
					content.pop(i)
					break
			last_line=content[-1]
			last_line_fixed=last_line.replace(r'!0','True').replace(r'!1','False').replace('null','None')
			values=re.search(re.compile(r'(?<=\}\().*?(?=\)(;)?\n)'),last_line_fixed)[0].split(', ')
			
			if len(values)>len(args):
				isArray=True
				values=re.findall(re.compile(r'(?<=(\s|\())(\[.*?\])(?=(,|\);))'),last_line_fixed) 
		
			#if any(ext in last_line_fixed for ext in JS_BUILTIN_FUNCTIONS):
			if JS_BUILTIN_FUNCTIONS in last_line_fixed:
				ctx = py_mini_racer.MiniRacer()
				for i in range(len(values)):
					if JS_BUILTIN_FUNCTIONS in values[i]:
						values[i]=ctx.eval('JSON.stringify('+values[i]+')')
			content.pop()
			file.seek(0)
			full_content=file.read().replace(first_line,'',1).replace(last_line,'',1)
		else:
			full_content=file.read()
			args=re.findall(re.compile(r'\'?0x\d[a-z0-9]{0,2}\'?'),full_content) 
			
		
		
		head, tail = os.path.split(path)
		new_file=os.path.join(os.path.dirname(__file__),'new_'+tail)
		with open (new_file,'w+',encoding='utf-8') as new_f: 
			index=0
			pattern=None
			for arg in args:
				if isArray:pattern=re.compile(arg.strip()+'\[\d{1,}\]')
				elif isHexadecimal:
					value=int(arg.replace("'",''), 16)
					if not any(arg in i and len(i)>len(arg) for i in args):
						full_content=re.sub(arg,str(value), full_content) 
					continue
				else:pattern=re.compile(arg.strip()+'\s')
				_result=re.findall(pattern, full_content)
				for r in _result:
					if isArray:value=eval(values[index][1])[int(re.search(re.compile(r'\d{1,}'),r)[0])] 
					else:value=eval(values[index])
					if isinstance(value,bool):value=str(value).lower()
					elif isinstance(value,str) and value!='undefined' and value!='object'  and value!='string' and value!='number' and value!='boolean' and value!='null':
						# if re.search(re.compile(r'\\u'),value):
							# value=re.sub(re.compile(r'(\\(?=u)|\\$)'),r'\\\\',value)
						if '\\' in value:value=value.replace('\\','\\\\')
						value=f'"{value}"'if '"' not in value else f"'{value}'"
						value=re.escape(str(value))
					
					full_content=re.sub(re.escape(r),' '+str(value), full_content)#re.escape(r)

				index+=1
			# try:
			new_f.writelines(full_content)
			# except UnicodeEncodeError:
				# full_content=full_content.replace('\ud83d','\\ud83d').replace('\ude03','\\ude03')
				# new_f.writelines(full_content)
			sys.exit()
		
		
		
		
if __name__ == '__main__' :
	parser=argparse.ArgumentParser(description=f'js de-obfuscate version {VERSION}')
	parser.add_argument('file',help='js file path')
	parser.add_argument('-H', '--hexadecimal', action='store_true',help='is replace hexadecimal')
	args = parser.parse_args()
	main(args.file,args.hexadecimal)