import threading
import tkinter as tk
from tkinter import ttk
from history import save_record
import ttkbootstrap as tb

_addbar_open = False




def show_addbar():
	global _addbar_open
	if _addbar_open:
		return
	t = threading.Thread(target=_show_addbar_tk, daemon=True)
	t.start()




def _show_addbar_tk():
	global _addbar_open
	if _addbar_open:
		return
	_addbar_open = True
	root = tb.Window(themename='cyborg')
	root.title('Novo registro')
	root.resizable(False, False)
	try:
		root.tk.call("tk", "scaling", 1.25)
	except Exception:
		pass


	# layout simples
	frm = ttk.Frame(root, padding=12)
	frm.pack(fill='both', expand=True)


	lbl = ttk.Label(frm, text='Título do objeto:')
	lbl.pack(anchor='w')


	entry = ttk.Entry(frm, width=60)
	entry.pack(fill='x')
	entry.focus_set()


	status_var = tk.StringVar(value='Para gravar')
	status_lbl = ttk.Label(frm, text='Status:')
	status_lbl.pack(anchor='w')
	status_cb = ttk.Combobox(frm, textvariable=status_var, values=['Para gravar', 'Pronto   '], state='readonly')
	status_cb.pack(fill='x')
	status_cb.current(0)


	help_lbl = ttk.Label(frm, text='Dica: você pode digitar "nome | status" e pressionar Enter para salvar')
	help_lbl.pack(anchor='e')


	def on_enter(event=None):
		text = entry.get().strip()
		if not text:
			return
		# Accept "nome | status" format
		status = status_var.get()
		if '|' in text:
			parts = [p.strip() for p in text.split('|', 1)]
			if len(parts) == 2 and parts[1]:
				candidate = parts[1].lower()
				if candidate in ('Para gravar', 'Pronto'):
					status = candidate
				text = parts[0]
		save_record(text, status)
		try:
			root.destroy()
		finally:
			_addbar_open = False


	entry.bind('<Return>', on_enter)


	# centraliza pequena janela
	root.update_idletasks()
	w = max(root.winfo_reqwidth(), 520)
	h = max(root.winfo_reqheight(), 160)
	x = (root.winfo_screenwidth() - w) // 2
	y = (root.winfo_screenheight() - h) // 2
	root.geometry(f'+{x}+{y}')
	try:
		root.attributes('-topmost', True)
	except Exception:
		pass


	try:
		root.mainloop()
	finally:
		_addbar_open = False