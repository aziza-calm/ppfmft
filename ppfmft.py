import Tkinter as tk
from pymol import cmd

def __init_plugin__(app):
    app.menuBar.addmenuitem('Plugin', 'command',
        label='Dock Plugin',
        command=lambda: mytkdialog(app.root))

#Action for button Start
#runs fmft_dock.py
def run_dock(dirname, recname, ligname):
	import subprocess
	import tkMessageBox
	import time
	import shutil
	import tempfile
	tmpdir = tempfile.mkdtemp(dir = dirname)
	rec = tmpdir + "/receptor.pdb"
	cmd.save(rec, recname)
	lig = tmpdir + "/ligand.pdb"
	cmd.save(lig, ligname)
	srcfmft = dirname + "/install-local/bin/fmft_dock.py"
	wei = dirname + "/install-local/bin/fmft_weights_ei.txt"
	fmftcmd = ['python', srcfmft, lig, rec, wei] 
	p = subprocess.Popen(fmftcmd, stderr=subprocess.PIPE)
	while p.returncode is None:
		time.sleep(1)
		s_out, s_err = p.communicate()
		if s_out:
			tkMessageBox.showinfo("Information", s_out)
		if s_err:
			tkMessageBox.showinfo("Warnings", s_err)
    	p.poll()
	if p.returncode == 0:
		tkMessageBox.showinfo("Information","Done! :)")
	else:
		tkMessageBox.showerror("Error","Something went wrong :(")
	shutil.rmtree(tmpdir)

def fmftpath(x, y):
	pathw = tk.Tk()
	pathw.title("Path")
	fmftpath_label = tk.Label(pathw, text="Specify the path to the /fmft_code_dev folder first")
	fmftpath_label.grid(row=2, column=0)
	fmftpath_entry = tk.Entry(pathw, width=50)
	fmftpath_entry.grid(row=3, column=0)
	fmftpath_entry.insert(0, "/home/aziza/Downloads/basa/fmft_code_dev")
	fmftpath_entry.bind('<Return>', run_dock)
	buttonDock=tk.Button(pathw,text='Start',width=6,height=1,bg='blue',fg='white',font='verdana 14', command = lambda: run_dock(fmftpath_entry.get(), x, y))
	buttonDock.grid(column=1,row=4)
	
def mytkdialog(parent):
	#we need ttk for comboboxes
	import ttk
	
	root = tk.Tk()
	root.geometry("500x200+100+80")
	root.title("Pymol future Dock Plugin")
	
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
	
 	buttonDock=tk.Button(root,text='Dock!',width=6,height=1,bg='blue',fg='white',font='arial 14', command = lambda:  fmftpath(rec, lig))
 	buttonDock.grid(column=2,row=1)
