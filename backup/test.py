import tkinter as tk
from tkinter.constants import DISABLED
from tkinter.filedialog import askopenfilename, asksaveasfilename

grey = "#36393f"
blurple = "#5261f8"
white = "#F0F0F0"
green = "#03c03c"
red = "#c23b22"

window = tk.Tk()
window.rowconfigure(0, minsize=200, weight=1)
window.columnconfigure(1, minsize=200, weight=1)

txt_edit = tk.Text(window, bg=grey, fg=white)
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2, bg=grey)

txt_edit.grid(row=0, column=1, sticky="nsew")
fr_buttons.grid(row=0, column=0, sticky="ns")

btn_send = tk.Button(fr_buttons, text="Send", state=DISABLED, bg=blurple, fg=white, relief="flat")
btn_edit = tk.Button(fr_buttons, text="Edit", bg=blurple, fg=white, relief="flat")
btn_delete = tk.Button(fr_buttons, text="Delete", bg=blurple, fg=white, relief="flat")
btn_logs = tk.Button(fr_buttons, text="Logs", bg=blurple, fg=white, relief="flat")

btn_logs.grid(row=0, column=0, sticky="ew", padx=3, pady=5)
btn_send.grid(row=1, column=0, sticky="ew", padx=3)
btn_edit.grid(row=2, column=0, sticky="ew", padx=3, pady=2)
btn_delete.grid(row=3, column=0, sticky="ew", padx=3)


lbl_guild = tk.Label(fr_buttons, text="Guild:", bg=grey, fg=white)
lbl_guild_name = tk.Label(fr_buttons, text="Guild", bg=grey, fg=blurple)
lbl_channel = tk.Label(fr_buttons, text="Channel:", bg=grey, fg=white)
lbl_channel_name = tk.Label(fr_buttons, text="Channel", bg=grey, fg=blurple)

lbl_guild.grid(row=4, column=0, sticky="s")
lbl_guild_name.grid(row=4, column=1, sticky="s")
lbl_channel.grid(row=5, column=0, sticky="s")
lbl_channel_name.grid(row=5, column=1, sticky="s")


lbl_status = tk.Label(fr_buttons, text="Status:", bg=grey, fg=white)
lbl_status_online = tk.Label(fr_buttons, text="Online", bg=grey, fg=green)

lbl_status.grid(row=6, column=0, sticky="ew")
lbl_status_online.grid(row=6, column=1, sticky="ew")

window.mainloop()