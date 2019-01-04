def __init_plugin__(app):
    app.menuBar.addmenuitem('Plugin', 'command',
        label='Pymol future Dock Plugin',
        command=lambda: mytkdialog(app.root))

#Action for button Dock! (the only button we have)
#runs fmft_dock.py
def leftmouse():
	import subprocess
	import Tkinter
	import tkMessageBox
	import time
	srcfmft = "/home/aziza/Downloads/basa/fmft_code_dev/install-local/bin/fmft_dock.py"
	lig = "/home/aziza/Downloads/basa/fmft_code_dev/install-local/bin/1avx_l_nmin.pdb"
	rec = "/home/aziza/Downloads/basa/fmft_code_dev/install-local/bin/1avx_r_nmin.pdb"
	wei = "/home/aziza/Downloads/basa/fmft_code_dev/install-local/bin/fmft_weights_ei.txt"
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
	
def mytkdialog(parent):
	import Tkinter as tk
	#we need ttk for comboboxes
	import ttk
	
	root = tk.Tk()
	root.geometry("500x200+100+80")
	root.title("Pymol future Dock Plugin")
	combobox1 = ttk.Combobox(root,values = [u"Desire", u"Lust"],height=3)
	combobox1.set(u"Receptor")
 	combobox1.grid(column=0,row=0)
 	combobox2 = ttk.Combobox(root, values = [u"ONE",u"TWO",u"THREE"],height=3)
 	combobox2.set(u"Ligand")
	combobox2.grid(column=2,row=0)
 	buttonDock=tk.Button(root,text='Dock!',width=6,height=1,bg='blue',fg='white',font='arial 14', command = leftmouse)
 	buttonDock.grid(column=2,row=1)
