import Tkinter as tk
import ttk	
from pymol import cmd
import pymol
import re
import subprocess
import tkMessageBox
import time
import shutil
import tempfile
from threading  import Thread
from Queue import Queue, Empty
import numpy as np
import os
import tkFileDialog

def __init_plugin__(app):
    app.menuBar.addmenuitem('Plugin', 'command',
        label='Dock them all',
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
	try:
		ft_data = np.loadtxt(ft_file)
		rm_data = np.loadtxt(rm_file)
	except IOError:
		tkMessageBox.showinfo("Warning!", "Unable to load ft_file, rm_file.\nCheck if the path is correct or if there is enough space")
		return 1
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
	cmd.mplay()


def pdb_prep(mol, out_prefix, tmpdir):
	#charmm_prm = "~/prms/charmm/charmm_param.prm"
	#charmm_rtf = "~/prms/charmm/charmm_param.rtf"
	
	sblu = ['/home/aziza/miniconda3/bin/sblu', 'pdb', 'prep', mol, '--no-minimize', '--out-prefix', out_prefix]
	p = subprocess.Popen(sblu, cwd=tmpdir)
	while p.poll() is None:  # While our process is running
		time.sleep(0.01)
	if p.returncode is not None:
		return tmpdir + "/" + out_prefix + ".pdb"


def choose_folder(s, fmftpath_entry):
	s = tkFileDialog.askdirectory()
	fmftpath_entry.delete(0, tk.END)
	fmftpath_entry.insert(0, s)
	pymol.plugins.pref_set("FMFT_PATH", s)


# an idiotic window asking you to enter the path
# useless for now, but may be used in the future
def _fmftpath():
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
	fmftpath = pymol.plugins.pref_get("FMFT_PATH", d=user_path)
	fmftpath_entry.insert(0, fmftpath)
	
	buttonChoose = tk.Button(pathw, text='Choose', command=lambda: choose_folder(fmftpath, fmftpath_entry))
	buttonChoose.grid(column=1, row=4)
	
	return fmftpath


def fmft_path():
	user_path = os.path.expanduser("~")
	fmftpath = pymol.plugins.pref_get("FMFT_PATH", d=user_path)
	return fmftpath


# runs fmft_dock.py
def run_dock(recname, ligname):
	# Checking if receptor or ligand were somehow removed
	if not recname in cmd.get_names(selection='(all)'):
		tkMessageBox.showinfo("Warning", "Selected receptor doesn't exist anymore :c")
		return 1
	if not ligname in cmd.get_names(selection='(all)'):
		tkMessageBox.showinfo("Warning", "Selected ligand doesn't exist anymore :c")
		return 1
	dirname = fmft_path()
	if dirname.find("fmft_code_dev") != (len(dirname) - 13) or dirname == os.path.expanduser("~"):
		print "Invalid path"
		tkMessageBox.showinfo("Invalid FMFT path", "Something wrong with FMFT path. Please, specify it in settings.")
		return 2
		
	# Creating a temporary directory
	tmpdir = tempfile.mkdtemp()
	
	# Making copies of receptor and ligand into tmpdir
	rec = tmpdir + "/receptor.pdb"
	cmd.save(rec, recname)
	rec_prep = pdb_prep(rec, "rec_prep", tmpdir)
	lig = tmpdir + "/ligand.pdb"
	cmd.save(lig, ligname)
	lig_prep = pdb_prep(lig, "lig_prep", tmpdir)
	
	# Preparations for running fmft (creating a string command for Popen)
	srcfmft = dirname + "/install-local/bin/fmft_dock.py"
	wei = dirname + "/install-local/bin/prms/fmft_weights_ei.txt"
	fmftcmd = ['python', srcfmft, lig_prep, rec_prep, wei]
	
	# Run!
	p = subprocess.Popen(fmftcmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=tmpdir)
	
	# Creating a window for dock log
	dockw = tk.Tk()
	dockw.title("FMFT: running...")
	text = tk.Text(dockw, width=90, height=70)
	text.grid(row=0, column=0)
	text.insert('1.0', "Started docking\nReceptor is {}\nLigand is {}\n".format(recname, ligname))
	text.insert('end', "FMFT path is {}\n".format(dirname))
	
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
	
	# When the process is terminated, show results
	if rc is not None:
		show_result(tmpdir, ligname)
		
	# Removing temporary directory
	shutil.rmtree(tmpdir)


def update_selection(comboboxRec, comboboxLig):
	comboboxRec['values'] = cmd.get_names(selection='(all)')
	comboboxLig['values'] = cmd.get_names(selection='(all)')


def settings():
	sett = tk.Tk()
	sett.title("Settings")
	
	fmftpath = fmft_path()
	fmftpath_label1 = tk.Label(sett, text="Specify the path to the /fmft_code_dev folder first")
	fmftpath_label2 = tk.Label(sett, text="Example:/home/aziza/Downloads/basa/fmft_code_dev")
	fmftpath_label1.grid(row=0, column=0)
	fmftpath_label2.grid(row=1, column=0)
	fmftpath_entry = tk.Entry(sett, width=45, textvariable=fmftpath)
	fmftpath_entry.grid(row=2, column=0)
	# this is a default path
	fmftpath_entry.insert(0, fmftpath)
	buttonChoose = tk.Button(sett, text='Change', command=lambda: choose_folder(fmftpath, fmftpath_entry))
	buttonChoose.grid(column=1, row=0)
	fmftpath_entry.bind('<Return>', run_dock)


# Here is the main window where you select receptor und ligand
def mytkdialog(parent):
	root = tk.Tk()
	root.geometry("500x200+100+80")
	root.title("Dock Plugin")
	try:
		root.iconbitmap('@idea.xbm')
	except tk.TclError:
		print "Some problems with icon, but still works"
	
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
						   command=lambda: run_dock(comboboxRec.get(), comboboxLig.get()))
	buttonDock.grid(column=2, row=1)
	
	buttonSet = tk.Button(root, text='Settings', height=1, command=lambda: settings())
	buttonSet.grid(column=1, row=1)
 