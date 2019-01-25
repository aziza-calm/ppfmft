import Tkinter as tk
import ttk	
from pymol import cmd
import re
import subprocess
import tkMessageBox
import time
import shutil
import tempfile
from threading  import Thread
from Queue import Queue
import numpy as np
import os
import tkFileDialog

def __init_plugin__(app):
    app.menuBar.addmenuitem('Plugin', 'command',
        label='Dock Plugin',
        command=lambda: mytkdialog(app.root))

def read_output(pipe, funcs):
	for line in iter(pipe.readline, b''):
		for func in funcs:
			func(line.decode('utf-8'))
	pipe.close()
	
# Getting an axis from rotation matrix. We need it to use cmd.rotate
def get_axis(rm):
	eig_values, eig_vectors = np.linalg.eig(rm)
	v_d = np.abs(eig_values - 1)
	idx = np.argmin(v_d)
	return np.float64(eig_vectors[:, idx])

# Getting an angle from rotation matrix
def get_angle(rm):
	return np.arccos(0.5*(np.trace(rm)-1))

# Results of docking
# Kinda movie: ligand jumps around receptor
def show_result(tmpdir, ligname):
	n = 10 # number of positions of ligand
	ft_file = tmpdir + "/ft.000.0.0"
	rm_file = tmpdir + "/rm.000.0.0"
	ft_data = np.loadtxt(ft_file)
	rm_data = np.loadtxt(rm_file)
	for i in range(n):
		num_state = i + 1
		name_copy = "copy_ligand_" + str(i)
		cmd.copy(name_copy, ligname)
		tv = ft_data[i, 1:4]
		rm = rm_data[i].reshape((3, 3))
		en = ft_data[i, 4]
		cmd.translate(list(tv), name_copy)
		cmd.rotate(list(get_axis(rm)), get_angle(rm), name_copy)
		cmd.create("result", name_copy, 0, num_state)
		cmd.delete(name_copy)
	result = tmpdir + "/result_dock.pdb"
	cmd.save(result, "result")
	cmd.mplay()

# Action for button Start
# runs fmft_dock.py
def run_dock(dirname, recname, ligname):
	
	# Creating a temporary directory
	tmpdir = tempfile.mkdtemp(dir = dirname)
	
	# Making copies of receptor and ligand into tmpdir
	rec = tmpdir + "/receptor.pdb"
	cmd.save(rec, recname)
	lig = tmpdir + "/ligand.pdb"
	cmd.save(lig, ligname)
	
	# Preparations for running fmft (creating a string command for Popen)
	srcfmft = dirname + "/install-local/bin/fmft_dock.py"
	wei = dirname + "/install-local/bin/fmft_weights_ei.txt"
	fmftcmd = ['python', srcfmft, lig, rec, wei] 
	
	# Run!
	p = subprocess.Popen(fmftcmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=tmpdir)
	
	# Creating a window for dock log
	dockw = tk.Tk()
	dockw.title("Docking")
	text = tk.Text(dockw, width=90, height=70)
	text.grid(row=0, column=0)
	text.insert('1.0', "Docking started...")
	
	# Catching log lines using threads and queue
	outs, errs = [], []
	q = Queue()
	stdout_thread = Thread(target=read_output, args=(p.stdout, [q.put, outs.append]))
	stderr_thread = Thread(target=read_output, args=(p.stderr, [q.put, errs.append]))
	for t in (stdout_thread, stderr_thread):
		t.daemon = True
		t.start()
	p.wait()
	q.put(None)
	outs = ' '.join(outs)
	errs = ' '.join(errs)
	for line in iter(q.get, None):
		changedline = re.sub(r'\r', '\n', line)
		text.insert('1.0', changedline)
	rc = p.returncode
	
	# When the process is terminated, show results
	if rc is not None:
		show_result(tmpdir, ligname)
		
	# Removing temporary directory
	#shutil.rmtree(tmpdir)
	
def choose_folder(s, fmftpath_entry):
	import Tkconstants, tkFileDialog
	s = tkFileDialog.askdirectory()
	fmftpath_entry.delete(0, tk.END)
	fmftpath_entry.insert(0, s)

# Action for button Dock :3 it's a kind of surprise.
# When you finally press the coveted button and wait for the start of the magic,
# but instead you get an idiotic window asking you to enter the path
def fmftpath(rec, lig):
	# New window
	pathw = tk.Tk()
	pathw.title("Path")
	fmftpath = tk.StringVar()
	fmftpath_label1 = tk.Label(pathw, text="Specify the path to the /fmft_code_dev folder first")
	fmftpath_label2 = tk.Label(pathw, text="Example:/home/aziza/Downloads/basa/fmft_code_dev")
	fmftpath_label1.grid(row=2, column=0)
	fmftpath_label2.grid(row=3, column=0)
	fmftpath_entry = tk.Entry(pathw, width=45, textvariable=fmftpath)
	fmftpath_entry.grid(row=4, column=0)
	# this is a default path
	user_path = os.path.expanduser("~")
	fmftpath_entry.insert(0, user_path)
	
	buttonChoose = tk.Button(pathw, text='Choose', command = lambda: choose_folder(fmftpath, fmftpath_entry))
	buttonChoose.grid(column=1, row=4)
	
	fmftpath_entry.bind('<Return>', run_dock)
	# true button that runs docking
	buttonStart=tk.Button(pathw,text='Start',width=6,height=1,bg='blue',fg='white',font='verdana 14', command = lambda: run_dock(fmftpath_entry.get(), rec, lig))
	buttonStart.grid(column=1,row=5)
	
# Here is the main window where you select receptor und ligand
def mytkdialog(parent):
	
	root = tk.Tk()
	root.geometry("500x200+100+80")
	root.title("Dock Plugin")
	root.iconbitmap('@idea.xbm')
	
	receptors = cmd.get_names(selection='(all)')
	combobox1 = ttk.Combobox(root,values = receptors, height=3, state = 'readonly')
	combobox1.set(u"Receptor")
	combobox1.grid(column=0,row=0)
	rec = receptors[combobox1.current()]
	
 	ligands = cmd.get_names(selection='(all)')
	combobox2 = ttk.Combobox(root, values = ligands, height=3, state = 'readonly')
	combobox2.set(u"Ligand")
	combobox2.grid(column=1,row=0)
	lig = ligands[combobox2.current()]
	
 	buttonDock=tk.Button(root,text='Dock!',width=6,height=1,bg='blue',fg='white',font='arial 14', command = lambda: fmftpath(rec, lig))
 	buttonDock.grid(column=2,row=1)
