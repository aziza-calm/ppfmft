import Tkinter as tk
from pymol import cmd

def __init_plugin__(app):
    app.menuBar.addmenuitem('Plugin', 'command',
        label='Dock Plugin',
        command=lambda: mytkdialog(app.root))

def read_output(pipe, funcs):
	for line in iter(pipe.readline, b''):
		for func in funcs:
			func(line.decode('utf-8'))
	pipe.close()

# Action for button Start
# runs fmft_dock.py
def run_dock(dirname, recname, ligname):
	import subprocess
	import tkMessageBox
	import time
	import shutil
	import tempfile
	from threading  import Thread
	from Queue import Queue
	# Creating of temporary directory where receptor and ligand will be copied in
	tmpdir = tempfile.mkdtemp(dir = dirname)
	rec = tmpdir + "/receptor.pdb"
	cmd.save(rec, recname)
	lig = tmpdir + "/ligand.pdb"
	cmd.save(lig, ligname)
	srcfmft = dirname + "/install-local/bin/fmft_dock.py"
	wei = dirname + "/install-local/bin/fmft_weights_ei.txt"
	fmftcmd = ['python', srcfmft, lig, rec, wei] 
	# Run!
	p = subprocess.Popen(fmftcmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=tmpdir)
	dockw = tk.Tk()
	dockw.title("Docking")
	text = tk.Text(dockw, width=90, height=70)
	text.grid(row=0, column=0)
	text.insert('1.0', "Docking started...")
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
		import re
		changedline = re.sub(r'\r', '\n', line)
		text.insert('1.0', changedline)
	rc = p.returncode
	# Removing temporary directory
	shutil.rmtree(tmpdir)

# Action for button Dock :3 it's a kind of surprise.
# When you finally press the coveted button and wait for the start of the magic,
# but instead you get an idiotic window asking you to enter the path
def fmftpath(rec, lig):
	pathw = tk.Tk()
	pathw.title("Path")
	fmftpath_label = tk.Label(pathw, text="Specify the path to the /fmft_code_dev folder first")
	fmftpath_label.grid(row=2, column=0)
	fmftpath_entry = tk.Entry(pathw, width=50)
	fmftpath_entry.grid(row=3, column=0)
	# this is a default path
	fmftpath_entry.insert(0, "/home/aziza/Downloads/basa/fmft_code_dev")
	fmftpath_entry.bind('<Return>', run_dock)
	# true button that runs docking
	buttonStart=tk.Button(pathw,text='Start',width=6,height=1,bg='blue',fg='white',font='verdana 14', command = lambda: run_dock(fmftpath_entry.get(), rec, lig))
	buttonStart.grid(column=1,row=4)
	
# Here is the main window where you select receptor und ligand
def mytkdialog(parent):
	#we need ttk for comboboxes
	import ttk
	
	root = tk.Tk()
	root.geometry("500x200+100+80")
	root.title("Dock Plugin")
	
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
