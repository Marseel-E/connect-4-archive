import tkinter as tk
from tkinter.constants import DISABLED, X


#- Variables
grey = "#36393f"
blurple = "#5261f8"
white = "#F0F0F0"
green = "#03c03c"
red = "#c23b22"


#- Functions
class Open:

    def guilds_window():
        swindow = tk.Tk()
        swindow.title("Selection")
        swindow.geometry('200x345')

        fr_search = tk.Frame(swindow, bg=grey)
        fr_search.grid(row=0, column=0)

        lbl_search = tk.Label(fr_search, text="Search", bg=grey, fg=blurple)
        lbl_search.grid(row=0, column=0, sticky="nsew")

        ety_search = tk.Entry(fr_search, text="search", bg=grey, fg=white, highlightthickness=2, highlightbackground=blurple, highlightcolor=blurple)
        ety_search.grid(row=1, column=0, ipadx=36)

        fr_selection = tk.Frame(swindow, bg=grey)
        fr_selection.grid(row=1, column=0, sticky="nsew")

        lbl_selection = tk.Label(fr_selection, text="Guilds", bg=grey, fg=blurple)
        lbl_selection.grid(row=0, column=0, sticky="nsew")

        box_selection = tk.Listbox(fr_selection, bg=grey, fg=white, highlightthickness=2, highlightbackground=blurple, highlightcolor=blurple, selectforeground=blurple, selectbackground=grey)
        box_selection.grid(row=1, column=0, ipadx=36, ipady=57)

        swindow.mainloop()
    
    def channels_window():
        swindow = tk.Tk()
        swindow.title("Selection")
        swindow.geometry('200x345')

        fr_search = tk.Frame(swindow, bg=grey)
        fr_search.grid(row=0, column=0)

        lbl_search = tk.Label(fr_search, text="Search", bg=grey, fg=blurple)
        lbl_search.grid(row=0, column=0, sticky="nsew")

        ety_search = tk.Entry(fr_search, text="search", bg=grey, fg=white, highlightthickness=2, highlightbackground=blurple, highlightcolor=blurple)
        ety_search.grid(row=1, column=0, ipadx=36)

        fr_selection = tk.Frame(swindow, bg=grey)
        fr_selection.grid(row=1, column=0, sticky="nsew")

        lbl_selection = tk.Label(fr_selection, text="Channels", bg=grey, fg=blurple)
        lbl_selection.grid(row=0, column=0, sticky="nsew")

        box_selection = tk.Listbox(fr_selection, bg=grey, fg=white, highlightthickness=2, highlightbackground=blurple, highlightcolor=blurple, selectforeground=blurple, selectbackground=grey)
        box_selection.grid(row=1, column=0, ipadx=36, ipady=57)

        swindow.mainloop()


#- Main window
window = tk.Tk()
window.title("Dev's den")
window.geometry('750x500')
window.rowconfigure(0, minsize=50, weight=1)
window.columnconfigure(1, minsize=100, weight=1)

#- Frames
txt_edit = tk.Entry(window, bg=grey, fg=white, highlightthickness=2, highlightbackground=blurple, highlightcolor=blurple)
txt_logs = tk.Listbox(window, bg=grey, fg=white, highlightthickness=2, highlightbackground=blurple, highlightcolor=blurple)
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=0, bg=grey)
fr_logs = tk.Frame(window, relief=tk.RAISED, bd=0, bg=grey)

txt_edit.grid(row=1, column=1, sticky="nsew")
txt_logs.grid(row=0, column=1, sticky="nsew")
fr_buttons.grid(row=1, column=0, sticky="nsew")
fr_logs.grid(row=0, column=0, sticky="nsew")

#- Buttons
btn_send = tk.Button(fr_buttons, text="Send", bg=green, fg=white, relief="flat", activebackground=grey, activeforeground=green)
btn_edit = tk.Button(fr_buttons, text="Edit", bg=blurple, fg=white, relief="flat", activebackground=grey, activeforeground=blurple)
btn_delete = tk.Button(fr_buttons, text="Delete", bg=red, fg=white, relief="flat", activebackground=grey, activeforeground=red)

btn_send.grid(row=1, column=0, sticky="ew", ipady=5, ipadx=79)
btn_edit.grid(row=2, column=0, sticky="ew", pady=5, ipady=5, ipadx=79)
btn_delete.grid(row=3, column=0, sticky="ew", ipady=5, ipadx=79)

#- Logs
btn_logs = tk.Button(fr_logs, text="Logs", bg=blurple, fg=white, relief="flat", activebackground=grey, activeforeground=blurple)

btn_logs.grid(row=1, column=0, sticky="ew", ipady=5, ipadx=83)

#- Guild, Channel & Status
lbl_guild_name = tk.Button(fr_logs, text="Guild", bg=grey, fg=blurple, relief="flat", command=Open.guilds_window, activebackground=grey, activeforeground=blurple)
lbl_channel_name = tk.Button(fr_logs, text="Channel", bg=grey, fg=blurple, relief="flat", command=Open.channels_window, activebackground=grey, activeforeground=blurple)
lbl_status = tk.Label(fr_logs, text="Status:", bg=grey, fg=white)
lbl_status_online = tk.Label(fr_logs, text="Online", bg=grey, fg=green)

lbl_guild_name.grid(row=2, column=0, sticky="nsew")
lbl_channel_name.grid(row=3, column=0, sticky="nsew")
lbl_status.grid(row=4, column=0, sticky="w", pady=273)
lbl_status_online.grid(row=4, column=0, sticky="w", padx=40)

window.mainloop()