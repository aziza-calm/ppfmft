def __init_plugin__(app):
    app.menuBar.addmenuitem('Plugin', 'command',
        label='Pymol future Dock Plugin',
        command=lambda: mytkdialog(app.root))

#Action for button Dock! (the only button we have)
#runs fmft_dock.py
def leftmouse():
	import subprocess
	srcfmft = "/home/aziza/Downloads/basa/fmft_code_dev/install-local/bin/fmft_dock.py"
	lig = "/home/aziza/Downloads/basa/fmft_code_dev/install-local/bin/1avx_l_nmin.pdb"
	rec = "/home/aziza/Downloads/basa/fmft_code_dev/install-local/bin/1avx_r_nmin.pdb"
	wei = "/home/aziza/Downloads/basa/fmft_code_dev/install-local/bin/fmft_weights_ei.txt"
	cmd = "python " + str(srcfmft) + " " + str(lig) + " " + str(rec) + " " + str(wei) 
	subprocess.Popen(cmd, shell=True)
	
def mytkdialog(parent):
	import Tkinter as tk
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
