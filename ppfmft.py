# /home/aziza/Downloads/basa/pymol/ppfmft/ppfmft.py
# /home/aziza/miniconda3/bin/sblu
from __future__ import print_function

from pymol import cmd
import pymol
import re
import subprocess
import time
import json
import numpy as np
import os
import shutil
import tempfile
from threading  import Thread
try:
	import Tkinter as tk
	import ttk  
	import tkMessageBox
	from Queue import Queue, Empty
	import tkFileDialog
except ImportError:
	import tkinter as tk
	from tkinter import ttk
	from tkinter import messagebox as tkMessageBox
	from tkinter import messagebox as tkFileDialog
	from queue import Queue, Empty

MEM_PER_PROC = 1.5  # GB
PROC_COUNT = pymol.plugins.pref_get("PROC_COUNT", d='4')
NRES = pymol.plugins.pref_get("NRES", d='1000')
NUMSHOW = pymol.plugins.pref_get("NUMSHOW", d='10')

def __init_plugin__(app):
	app.menuBar.addmenuitem('Plugin', 'command',
		label='Dock them all',
		command=lambda: mytkdialog(app.root))


def memory():
	# Get node total memory and memory usage
	with open('/proc/meminfo', 'r') as mem:
		ret = {}
		tmp_free = 0
		for i in mem:
			sline = i.split()
			if sline[0] == 'MemTotal:':
				ret['total'] = sline[1]
			elif sline[0] in ('MemFree:', 'Buffers:', 'Cached:'):
				tmp_free += int(sline[1])
		ret['free'] = tmp_free
		ret['used'] = int(ret['total']) - ret['free']
	return ret


def read_output(pipe, funcs):
	for line in iter(pipe.readline, b''):
		for func in funcs:
			func(line.decode('utf-8'))
	pipe.close()


# Results of docking
# Kinda movie: ligand jumps around receptor
def show_result(tmpdir, ligname):
	NUMSHOW = pymol.plugins.pref_get("NUMSHOW", d='10') # number of positions of ligand
	ft_file = tmpdir + "/ft.000.0.0"
	rm_file = tmpdir + "/rm.000.0.0"
	try:
		ft_data = np.loadtxt(ft_file)
		rm_data = np.loadtxt(rm_file)
	except IOError:
		tkMessageBox.showinfo("Warning!", "Unable to load ft_file, rm_file.\nCheck if the path is correct or if there is enough space")
		return None

	# Reading clustering result
	clusters_path = tmpdir + "/clusters.000.0.0.json"
	with open(clusters_path, "r") as clusters_file:
		clusters = json.load(clusters_file)
	centers = []
	for dic in clusters['clusters']:
		centers.append(dic['center'])

	result_name = "result"
	if result_name in cmd.get_names(selection='(all)'):
		i = 1
		result_name = "result_" + str(i)
		while result_name in cmd.get_names(selection='(all)'):
			i += 1
			result_name = "result_" + str(i)
	print(int(NUMSHOW))

	# showing n centers
	sblupath = sblu_path()
	sblu_mod = [sblupath, 'docking', 'gen_cluster_pdb', clusters_path, ft_file, rm_file, ligname]
	print(sblu_mod)
	p = subprocess.Popen(sblu_mod, cwd=tmpdir)
	print("Build cluster models")
	while p.poll() is None:
		time.sleep(0.01)
	for i in range(int(NUMSHOW)):
		num_state = i + 1
		name_copy = "copy_ligand_" + str(i)
		lig_load = tmpdir + "/lig.0" + str(i) + ".pdb"
		cmd.load(lig_load, name_copy)
		cmd.create(result_name, name_copy, 0, num_state)
		cmd.delete(name_copy)
	cmd.mplay()


# Preprocessing
def pdb_prep(mol, out_prefix, tmpdir):
	#charmm_prm = "~/prms/charmm/charmm_param.prm"
	#charmm_rtf = "~/prms/charmm/charmm_param.rtf"
	sblupath = sblu_path()
	if os.path.basename(sblupath) != 'sblu' or not os.path.isfile(sblupath) or not os.access(sblupath, os.X_OK):
		print(sblupath)
		tkMessageBox.showinfo("Wrong path", "SBLU path is invalid")
		return None
	sblu = [sblupath, 'pdb', 'prep', mol, '--no-minimize', '--out-prefix', out_prefix]
	print("Preprocessing started")
	p = subprocess.Popen(sblu, cwd=tmpdir)
	while p.poll() is None:  # While our process is running
		time.sleep(0.01)
	if p.returncode is not None:
		return tmpdir + "/" + out_prefix + ".pdb"


# Saving in config whether preprocessing is needed
def save_prep(key, s):
	pymol.plugins.pref_set(key, s)


# Auxiliary function for ui-choosing of folder
def choose_folder(s, path_entry, key):
	path_entry['state'] = 'normal'
	s = tkFileDialog.askdirectory()
	path_entry.delete(0, tk.END)
	path_entry.insert(0, s)
	pymol.plugins.pref_set(key, s)
	path_entry['state'] = 'readonly'


# Getting fmft path from config file
def fmft_path():
	user_path = os.path.expanduser("~")
	fmftpath = pymol.plugins.pref_get("FMFT_PATH", d=user_path)
	return fmftpath


# Getting sblu path from config file
def sblu_path():
	user_path = os.path.expanduser("~")
	sblupath = pymol.plugins.pref_get("SBLU_PATH", d=user_path)
	return sblupath


# Checking if fmft path is valid.
# It should end with fmft_code_dev and shouldn't be equal to home path (that is default)
def not_fmftpath(fmftpath):
	if os.path.basename(fmftpath) != 'fmft_suite' or not os.path.isdir(fmftpath):
		return 1
	else:
		return 0


def need_preprocessing(key, mol):
	if mol in str(pymol.plugins.pref_get(key)):
		return 1
	else:
		print(mol + " without preprocess")
		return 0


def cluster_result(tmpdir, ligname):
	sblupath = sblu_path()
	if os.path.basename(sblupath) != 'sblu' or not os.path.isfile(sblupath) or not os.access(sblupath, os.X_OK):
		print(sblupath)
		tkMessageBox.showinfo("Wrong path", "SBLU path is invalid")
		return None
	sblu = [sblupath, 'measure', 'pwrmsd', '-o', 'pwrmsd.000.0.0', ligname, 'ft.000.0.0', 'rm.000.0.0']
	print("Clustering started")
	p = subprocess.check_call(sblu, cwd=tmpdir)
	sblu = [sblupath, 'docking', 'cluster', '--json', '-o', 'clusters.000.0.0.json', 'pwrmsd.000.0.0']
	p = subprocess.check_call(sblu, cwd=tmpdir)


def change_proc(recname, ligname):
	proc = tk.Tk()
	# Number of cpu cores to use for computation
	proc_label = tk.Label(proc, text="Number of cpu cores to use for computation")
	proc_label.grid(column=0, row=0, columnspan=2)
	proc_entry = tk.Entry(proc, width=10)
	proc_entry.grid(row=1, column=0)
	PROC_COUNT = pymol.plugins.pref_get("PROC_COUNT", d='4')
	proc_entry.insert(0, PROC_COUNT)

	proc_button = tk.Button(proc, text='Confirm', command=lambda: save_prep("PROC_COUNT", proc_entry.get()))
	proc_button.grid(row=1, column=1)

	bContinue = tk.Button(proc, text="Continue", command=lambda: run_dock(recname, ligname))
	bContinue.grid(row=2, column=1)


def mem_check(recname, ligname):
	PROC_COUNT = pymol.plugins.pref_get("PROC_COUNT", d='4')
	# Checking free RAM
	try:
		mem = memory()
		if mem['free']/1024.0/1024.0 < int(PROC_COUNT) * MEM_PER_PROC:
			memw = tk.Tk()
			memw.title("Memory")
			mem_label = tk.Label(memw, text="Are you sure you want to use so many cores? Seems like you don't have enough memory")
			mem_label.grid()
			bSettings = tk.Button(memw, text="Settings", command=lambda: change_proc(recname, ligname))
			bSettings.grid()
		else:
			run_dock(recname, ligname)
	except:
		pass


# runs fmft_dock.py
def run_dock(recname, ligname):
	# Checking if receptor or ligand were somehow removed
	if not recname in cmd.get_names(selection='(all)'):
		tkMessageBox.showinfo("Warning", "Selected receptor doesn't exist anymore :c")
		return None
	if not ligname in cmd.get_names(selection='(all)'):
		tkMessageBox.showinfo("Warning", "Selected ligand doesn't exist anymore :c")
		return None
	dirname = fmft_path()
	if not_fmftpath(dirname):
		print("Invalid FMFT path")
		tkMessageBox.showinfo("Invalid FMFT path", "Something wrong with FMFT path. Please, specify it in settings.")
		return None

	if not os.path.isfile(dirname + '/install-local/bin/fmft_dock.py'):
		tkMessageBox.showinfo("FMFT", "Maybe you forgot to run ./bootstrap.sh?")
		return None

	# Creating a window for dock log
	dockw = tk.Tk()
	dockw.title("FMFT: running...")
	text = tk.Text(dockw, width=90, height=70)
	text.grid(row=0, column=0)
	text.insert('1.0', "Started docking\nReceptor is {}\nLigand is {}\n".format(recname, ligname))
	text.insert('end', "FMFT path is {}\n".format(dirname))

	# Creating a temporary directory
	tmpdir = tempfile.mkdtemp()

	# Making copies of receptor and ligand into tmpdir
	rec = tmpdir + "/receptor.pdb"
	cmd.save(rec, recname)
	# Preprocess receptor if needed
	if need_preprocessing("PREPROCESS", "receptor"):
		if pdb_prep(rec, "rec_prep", tmpdir) == -1:
			return
		rec = pdb_prep(rec, "rec_prep", tmpdir)
		text.insert('end', "Receptor preprocessed\n")
	lig = tmpdir + "/ligand.pdb"
	cmd.save(lig, ligname)
	# Preprocess ligand if needed
	if need_preprocessing("PREPROCESS", "ligand"):
		if pdb_prep(lig, "lig_prep", tmpdir) == -1:
			return
		lig = pdb_prep(lig, "lig_prep", tmpdir)
		text.insert('end', "Ligand preprocessed\n")

	# Preparations for running fmft (creating a string command for Popen)
	srcfmft = dirname + "/install-local/bin/fmft_dock.py"
	wei = dirname + "/install-local/bin/prms/fmft_weights_ei.txt"
	NRES = pymol.plugins.pref_get("NRES", d='1000')
	fmftcmd = ['python', srcfmft, '--proc_count', PROC_COUNT, '--nres', NRES, lig, rec, wei]
	print(fmftcmd)
	# Run!
	p = subprocess.Popen(fmftcmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=tmpdir)

	# Catching log lines using threads and queue
	outs, errs = [], []
	q = Queue()
	stdout_thread = Thread(target=read_output, args=(p.stdout, [q.put, outs.append]))
	stderr_thread = Thread(target=read_output, args=(p.stderr, [q.put, errs.append]))
	for t in (stdout_thread, stderr_thread):
		t.daemon = True
		t.start()

	while p.poll() is None:  # While our process is running
		time.sleep(0.01)
		while True:  # Read all elements currently in Queue
			try:
				line = q.get_nowait()
				changedline = re.sub(r'\r', '\n', line)
				text.insert('end', changedline)
			except Empty:
				break
		try:
			dockw.update()  # Tell GUI to update so it does not freeze
		except tk.TclError:
			tkMessageBox.showinfo("Warning", "You won't be able to see the log :(")
			break

	rc = p.returncode
	try:
		if rc == 0: dockw.title("FMFT: finished")
		else: dockw.title("FMFT: failed")
	except tk.TclError:
		pass

	# Cluster results
	cluster_result(tmpdir, lig)

	# When the process is terminated, show results
	if rc is not None:
		show_result(tmpdir, lig)

	# Removing temporary directory
	#shutil.rmtree(tmpdir)


def update_selection(comboboxRec, comboboxLig):
	comboboxRec['values'] = cmd.get_names(selection='(all)')
	comboboxLig['values'] = cmd.get_names(selection='(all)')


def settings():
	sett = tk.Tk()
	sett.title("Settings")

	# FMFT path
	fmftpath = fmft_path()
	fmftpath_label1 = tk.Label(sett, text="Specify the path to the /fmft_suite")
	fmftpath_label2 = tk.Label(sett, text="Example:/home/aziza/Downloads/basa/fmft_suite")
	fmftpath_label1.grid(row=0, column=0)
	fmftpath_label2.grid(row=1, column=0)
	fmftpath_entry = tk.Entry(sett, width=40, textvariable=fmftpath)
	fmftpath_entry.grid(row=2, column=0)
	# this is a default path
	fmftpath_entry.insert(0, fmftpath)
	fmftpath_entry['state'] = 'readonly'
	buttonChooseFmft = tk.Button(sett, text='Change', command=lambda: choose_folder(fmftpath, fmftpath_entry, "FMFT_PATH"))
	buttonChooseFmft.grid(column=1, row=2)
	fmftpath_entry.bind('<Return>', run_dock)

	variants = ['only ligand', 'only receptor', 'ligand and receptor', 'no preprocess']
	prepr_label = tk.Label(sett, text = "Make preprocess for").grid(column=0, row=3)
	prepr_com = ttk.Combobox(sett, values = variants, state='readonly')
	prepr_com.grid(column=0, row=4)
	prepr_com.set(str(pymol.plugins.pref_get("PREPROCESS", d='ligand and receptor')))
	#prepr_com.bind('<<ComboboxSelected>>', save_prep)
	bSave = tk.Button(sett, text='Change', command=lambda: save_prep("PREPROCESS", prepr_com.get()))
	bSave.grid(column=1, row=4)

	# sblu path
	sblu_label = tk.Label(sett, text="Specify the path to /sblu")
	sblu_label.grid(row=5, column=0)
	sblupath = sblu_path()
	sblupath_entry = tk.Entry(sett, width=40, textvariable=sblupath)
	sblupath_entry.grid(row=6, column=0)
	sblupath_entry.insert(0, sblupath)
	sblupath_entry['state'] = 'readonly'
	buttonChooseSblu = tk.Button(sett, text='Change', command=lambda: choose_folder(sblupath, sblupath_entry, "SBLU_PATH"))
	buttonChooseSblu.grid(row=6, column=1)

	# Number of cpu cores to use for computation
	proc_label = tk.Label(sett, text="Number of cpu cores to use for computation")
	proc_label.grid(column=0, row=7, columnspan=2)
	proc_entry = tk.Entry(sett, width=10)
	proc_entry.grid(row=8, column=0)
	PROC_COUNT = pymol.plugins.pref_get("PROC_COUNT", d='4')
	proc_entry.insert(0, PROC_COUNT)

	proc_button = tk.Button(sett, text='Change', command=lambda: save_prep("PROC_COUNT", proc_entry.get()))
	proc_button.grid(row=8, column=1)

	# NRES parameter of fmft_suite
	nres_label = tk.Label(sett, text="NRES parameter of fmft_suite")
	nres_label.grid(column=0, row=9, columnspan=2)
	nres_entry = tk.Entry(sett, width=10)
	nres_entry.grid(row=10, column=0)
	NRES = pymol.plugins.pref_get("NRES", d='1000')
	nres_entry.insert(0, NRES)

	nres_button = tk.Button(sett, text='Change', command=lambda: save_prep("NRES", nres_entry.get()))
	nres_button.grid(row=10, column=1)


# Here is the main window where you select receptor und ligand
def mytkdialog(parent):
	root = tk.Tk()
	root.geometry("500x200+100+80")
	root.title("Dock Plugin")
	try:
		root.iconbitmap('@idea.xbm')
	except tk.TclError:
		print("Some problems with icon, but still works")

	# Check if it's the first run
	user_path = os.path.expanduser("~")
	if os.path.exists(user_path + "/.pymolpluginsrc.py"):
		with open(user_path + "/.pymolpluginsrc.py") as plug:
			if not 'FMFT_PATH' in plug.read():
				settings()
	else:
		print("No config file!")
		settings()

	# Check if translation matrices are precomputed
	fmftpath = fmft_path()
	if os.path.exists(fmftpath + '/install-local/fmft_data/'):
		if not os.listdir(fmftpath + '/install-local/fmft_data/'):
			tkMessageBox.showinfo("Warning", "No translation matrices!")
			return
	else:
		tkMessageBox.showinfo("Warning", "Couldn't find {your_fmft_path}/install-local/fmft_data/")
		return

	selections = cmd.get_names(selection='(all)')

	comboboxRec = ttk.Combobox(root, values=selections, height=3, state='readonly')
	comboboxRec.set(u"Receptor")
	comboboxRec.grid(column=0, row=0)

	comboboxLig = ttk.Combobox(root, values=selections, height=3, state='readonly')
	comboboxLig.set(u"Ligand")
	comboboxLig.grid(column=1, row=0)

	buttonUpd = tk.Button(root, text='Update list', height=1, command=lambda: update_selection(comboboxRec, comboboxLig));
	buttonUpd.grid(column=2, row=0);

	buttonDock = tk.Button(root, text='Dock!', width=6, height=1, bg='blue', fg='white', font='arial 14',
							command=lambda: mem_check(comboboxRec.get(), comboboxLig.get()))
	buttonDock.grid(column=2, row=3)

	buttonSet = tk.Button(root, text='Settings', height=1, command=lambda: settings())
	buttonSet.grid(column=1, row=3)

	# Number of results to show in the output
	nres_label = tk.Label(root, text="Number of results to show in the output")
	nres_label.grid(column=0, row=1, columnspan=2)
	nres_entry = tk.Entry(root, width=10)
	nres_entry.grid(row=2, column=0)
	NUMSHOW = pymol.plugins.pref_get("NUMSHOW", d='10')
	nres_entry.insert(0, NUMSHOW)

	nres_button = tk.Button(root, text='Confirm', command=lambda: save_prep("NUMSHOW", nres_entry.get()))
	nres_button.grid(row=2, column=1)