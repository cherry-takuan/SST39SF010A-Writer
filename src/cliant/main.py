import tkinter as tk
import tkinter.scrolledtext as st
import tkinter.messagebox as tkmsg
import random
from tkinter import ttk
import numpy
from time import sleep

import tkinter.filedialog as dlg

import serial
from serial.tools import list_ports
import threading

import Baker
import numpy as np

import chardet

class Main:
    def __init__(self, root):
        self.NO_DATA = 0x100

        # データ設定
        self.total_row = 8*1024
        self.total_col = 16
        self.sector_size = 4*1024/16

        self.rom  = np.full((128*1024), self.NO_DATA, dtype=np.uint16)
        self.file = np.full((128*1024), self.NO_DATA, dtype=np.uint16)

        self.root = root
        self.version = "0.01"
        self.soft_name = "Flash Bakery (EEPROM Reader/Writer) [v" + self.version + "]"

        # ウィンドウ設定
        self.root.title(self.soft_name)
        self.root.geometry("500x600")
        self.root.resizable(width=True, height=True)
        self.root.minsize(400, 600)

        self.baker = Baker.baker()

        # メインウィンドウ生成
        nb = ttk.Notebook(self.root)
        # タブフレームの作成
        tab1 = tk.Frame(nb)
        tab2 = tk.Frame(nb)
        tab3 = tk.Frame(nb)
        # フレームウィジェットをタブとして Notebook に追加
        nb.add(tab1, text=' ROM viewer ')
        nb.add(tab2, text=' File viewer ')
        nb.add(tab3, text=' debug window ')
        # Notebook をウィンドウに配置（grid に変更）
        nb.grid(row=0, column=0, sticky="nsew")

        # tab1の生成
        # アドレス入力欄
        self.entry1 = tk.Entry(tab1)
        self.entry1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        # ボタン類
        btn_move = tk.Button(tab1, text="Move", command=self.rom_view_scroll)
        btn_Sload = tk.Button(tab1, text="sector load", command=self.rom_view_scroll)
        btn_load = tk.Button(tab1, text="all load", command=self.rom_read)
        btn_Sdel = tk.Button(tab1, text="sector del", command=self.rom_view_scroll)
        btn_del = tk.Button(tab1, text="all del", command=self.rom_del)

        btn_move.grid(row=0, column=1, padx=5, pady=5)
        btn_Sload.grid(row=0, column=2, padx=5, pady=5)
        btn_load.grid(row=0, column=3, padx=5, pady=5)
        btn_Sdel.grid(row=0, column=4, padx=5, pady=5)
        btn_del.grid(row=0, column=5, padx=5, pady=5)

        # ScrolledText ウィジェット
        self.rom_view = st.ScrolledText(tab1, wrap=tk.NONE, height=30)
        self.rom_view.grid(row=1, column=0, columnspan=6, sticky="nsew")

        # 横スクロールバーの追加
        self.h_scrollbar1 = tk.Scrollbar(tab1, orient=tk.HORIZONTAL, command=self.rom_view.xview)
        self.h_scrollbar1.grid(row=2, column=0, columnspan=6, sticky="ew")

        self.rom_view.config(xscrollcommand=self.h_scrollbar1.set)
        self.rom_view.config(state=tk.DISABLED)

        # レイアウトの調整（tab1 の行・列のサイズを可変にする）
        tab1.grid_rowconfigure(1, weight=1)
        tab1.grid_columnconfigure(0, weight=1)


        # tab2の生成
        # アドレス入力欄
        self.entry2 = tk.Entry(tab2)
        self.entry2.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        # ボタン類
        btn_move = tk.Button(tab2, text="Move", command=self.file_view_scroll)
        btn_Swrite = tk.Button(tab2, text="sector write", command=self.file_view_scroll)
        btn_write = tk.Button(tab2, text="all write", command=self.rom_write)

        btn_move.grid(row=0, column=1, padx=5, pady=5)
        btn_Swrite.grid(row=0, column=2, padx=5, pady=5,columnspan=2)
        btn_write.grid(row=0, column=4, padx=5, pady=5,columnspan=2)

        # ScrolledText ウィジェット
        self.file_view = st.ScrolledText(tab2, wrap=tk.NONE, height=30)
        self.file_view.grid(row=1, column=0, columnspan=6, sticky="nsew")

        # 横スクロールバーの追加
        self.h_scrollbar2 = tk.Scrollbar(tab2, orient=tk.HORIZONTAL, command=self.file_view.xview)
        self.h_scrollbar2.grid(row=2, column=0, columnspan=6, sticky="ew")

        self.file_view.config(xscrollcommand=self.h_scrollbar2.set)
        self.file_view.config(state=tk.DISABLED)

        # レイアウトの調整（tab2 の行・列のサイズを可変にする）
        tab2.grid_rowconfigure(1, weight=1)
        tab2.grid_columnconfigure(0, weight=1)



        # tab3の生成
        # ScrolledText ウィジェット
        self.debug_view = st.ScrolledText(tab3, wrap=tk.NONE, height=30)
        self.debug_view.grid(row=0, column=0,sticky="nsew")

        # 横スクロールバーの追加
        self.h_scrollbar = tk.Scrollbar(tab3, orient=tk.HORIZONTAL, command=self.debug_view.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.debug_view.config(xscrollcommand=self.h_scrollbar.set)
        self.debug_view.config(state=tk.DISABLED)

        # レイアウトの調整（tab1 の行・列のサイズを可変にする）
        tab3.grid_rowconfigure(0, weight=1)
        tab3.grid_columnconfigure(0, weight=1)
        self.debug_view.config(state=tk.NORMAL)
        self.debug_view.insert(tk.END, "準備完了\n")


        # メインウィンドウステータスバー
        self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=100, mode="determinate")
        self.progress_bar.grid(row=3, column=0, sticky="ew")
        self.status_bar = tk.Label(self.root, text="準備完了...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=2, column=0, sticky="ew")

        self.progress_bar["value"] = 0

        # ウィンドウのサイズ調整
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # 設定画面設定
        
        self.baker_form = Baker_setup(self)

       # メニュー生成
        self.menu = tk.Menu()
        self.files = tk.Menu(self.menu, tearoff=0)
        self.setup = tk.Menu(self.menu, tearoff=0)
        self.tools = tk.Menu(self.menu, tearoff=0)
        self.edit = tk.Menu(self.menu, tearoff=0)

        self.files.add_command(label='open', command=lambda : self.file_open(dlg.askopenfilename(title="file open")))
        self.files.add_command(label='save', command=self.quit)
        self.files.add_command(label='save as...', command=self.quit)
        self.menu.add_cascade(label='ファイル', menu=self.files)

        self.edit.add_command(label='検索')
        self.edit.add_command(label='置換')
        self.menu.add_cascade(label='編集', menu=self.edit)

        self.setup.add_command(label='情報', command=self.info_window)
        self.setup.add_command(label='終了', command=self.quit)
        self.setup.add_command(label='Baker設定', command=self.baker_form.view_open)
        self.menu.add_cascade(label='セットアップ', menu=self.setup)

        self.tools.add_command(label='比較', command=self.quit)
        self.menu.add_cascade(label='ツール', menu=self.tools)

        self.root.config(menu=self.menu)

        # 初期データロード
        self.rom_update()
        self.file_update()
    def scroll_to_top(self,view,line):
        view.see(f"{line}.0")  # まず see で行を可視化
        view.update_idletasks()  # 画面更新

        # 全体の行数を取得し、スクロール割合を計算
        total_lines = int(view.index(tk.END).split(".")[0]) - 1
        fraction = (line - 1) / total_lines  # `fraction` は 0.0 ~ 1.0 の範囲
        view.yview_moveto(fraction)  # 指定行を一番上に
    
    def rom_view_scroll(self):
        if self.entry1.get()[0:2] == "0x":
            line = int(int(self.entry1.get()[2:],16) >>4)
            self.scroll_to_top(self.rom_view, int(line + line/self.sector_size+1)+1)
        elif self.entry1.get()[0:7] == "sector:":
            line = int(self.entry1.get()[7:],10)*0x100
            self.scroll_to_top(self.rom_view,int(line + line/self.sector_size+1))
        else:
            line = int(self.entry1.get(),10)*0x100
            self.scroll_to_top(self.rom_view,int(line + line/self.sector_size+1))
    
    def file_view_scroll(self):
        if self.entry2.get()[0:2] == "0x":
            line = int(int(self.entry2.get()[2:],16) >>4)
            self.scroll_to_top(self.file_view, int(line + line/self.sector_size+1)+1)
        elif self.entry2.get()[0:7] == "sector:":
            line = int(self.entry2.get()[7:],10)*0x100
            self.scroll_to_top(self.file_view, int(line + line/self.sector_size+1))
        else:
            line = int(self.entry2.get(),10)*0x100
            self.scroll_to_top(self.file_view, int(line + line/self.sector_size+1))
    
    def rom_del(self):
        self.status_bar["text"] = "消去準備中…"
        read_thread = threading.Thread(target=self.rom_del_th, daemon=True)
        read_thread.start()
    def rom_del_th(self):
        self.status_bar["text"] = "消去中…"
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(10)
        sleep(1)
        result = self.baker.erase_all()
        self.status_bar["text"] = "消去完了"
        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate")
        self.progress_bar["value"] = 0
        self.progress_bar.update()

    def rom_read(self):
        self.status_bar["text"] = "読み取り準備中…"
        read_thread = threading.Thread(target=self.rom_read_th, daemon=True)
        read_thread.start()
    def rom_read_th(self):
        self.status_bar["text"] = "ROM Reading..."
        self.baker.address_set(0x00)
        self.rom.fill(self.NO_DATA)
        for count in range(self.total_row):
            self.rom[count] = self.baker.read()
            self.progress_bar["value"] = count / (self.total_row)*100
            self.progress_bar.update()
        self.status_bar["text"] = "読み取り完了"
        self.rom_update()
    
    def rom_write(self):
        self.status_bar["text"] = "書き込み準備中…"
        read_thread = threading.Thread(target=self.rom_write_th, daemon=True)
        read_thread.start()
    def rom_write_th(self):
        self.status_bar["text"] = "ROM Writing..."
        write_size = np.argmax(self.file == self.NO_DATA)
        self.debug_view.insert(tk.END, "書き込みサイズ:"+str(write_size)+"Byte")
        self.baker.address_set(0x00)
        for count in range(write_size):
            self.rom[count] = self.baker.write(self.file[count])
            self.progress_bar["value"] = count / (write_size)*100
            self.progress_bar.update()
        self.status_bar["text"] = "書き込み完了"
        self.rom_update()

    def rom_update(self):
        self.rom_view.config(state=tk.NORMAL)
        self.rom_view.tag_config('error', foreground="white", background="red")
        self.rom_view.delete("1.0", tk.END)
        count = 0
        for i in range(self.total_row):
            if i % self.sector_size == 0:
                data = "------  |  "
                for dmy in range(self.total_col):
                    data += "----"
                data += "    sector:" + str(int(i/self.sector_size))
                data += "\n"
                self.rom_view.insert(tk.END, data)
            # アドレス表示
            data = f"{(i<<4):06X}  |  "
            self.rom_view.insert(tk.END, data)
            # データ表示
            for dmy in range(self.total_col):
                if self.rom[count] == self.NO_DATA:
                    data = f"??  "
                    self.rom_view.insert(tk.END, data)
                else:
                    data = f"{self.rom[count] & 0xFF:02X}  "
                    if self.rom[count] == self.file[count]:
                        self.rom_view.insert(tk.END, data)
                    else:
                        self.rom_view.insert(tk.END, data, "error")
                count+=1

                #if random.randint(0, 1) == 0:
                #    self.rom_view.insert(tk.END, data)
                #else:
                #    self.rom_view.insert(tk.END, data, "error")
            data = "\n"
            self.rom_view.insert(tk.END, data)

        self.rom_view.config(state=tk.DISABLED)
    def file_open(self,file_path):
        self.rom_view.config(state=tk.NORMAL)
        self.rom_view.tag_config('error', foreground="white", background="red")
        print(file_path)
        with open(file_path, 'rb') as f:
            b = f.read()
            count = 0
            for data in b:
                self.file[count] = data
                count+=1
        self.file_update()
    def file_update(self):
        self.file_view.config(state=tk.NORMAL)
        self.file_view.delete("1.0", tk.END)
        self.file_view.tag_config('error', foreground="white", background="red")

        count = 0
        for i in range(self.total_row):
            if i % self.sector_size == 0:
                data = "------  |  "
                for dmy in range(self.total_col):
                    data += "----"
                data += "    sector:" + str(int(i/self.sector_size))
                data += "\n"
                self.file_view.insert(tk.END, data)
            # アドレス表示
            data = f"{(i<<4):06X}  |  "
            self.file_view.insert(tk.END, data)
            # データ表示
            for dmy in range(self.total_col):
                if self.file[count] == self.NO_DATA:
                    data = f"??  "
                else:
                    data = f"{self.file[count] & 0xFF:02X}  "
                count+=1
                self.file_view.insert(tk.END, data)
                #if random.randint(0, 1) == 0:
                #    self.file_view.insert(tk.END, data)
                #else:
                #    self.file_view.insert(tk.END, data, "error")
            data = "\n"
            self.file_view.insert(tk.END, data)

        self.file_view.config(state=tk.DISABLED)
    def info_window(self):
        tkmsg.showinfo(title="info", message=self.soft_name + "\n\nCopyright 2025 Cherry TAKUAN")

    def quit(self):
        del self.baker
        self.baker_form.quit()
        self.root.quit()


class Baker_setup:
    def __init__(self,parent):
        self.root = tk.Toplevel()
        self.parent = parent
        
        self.soft_name = "Baker設定"

        #ウィンドウ生成
        self.root.title(self.soft_name)
        self.root.geometry("300x100")
        self.root.resizable(width=False, height=False)

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        # シリアルポート選択メニュー
        self.port_var = tk.StringVar(self.root)
        self.port_menu = tk.OptionMenu(self.root, self.port_var, '')
        self.port_menu.grid(column=0,row=0,sticky="ew",padx=5, pady=5)

        # 接続/切断ボタン
        toggle_button = tk.Button(self.root, text="接続",command=self.dev_open)
        toggle_button.grid(column=1,row=0,padx=5, pady=5)

        text = tk.Label(self.root, text="バージョン情報")
        text.grid(row=1, column=0, columnspan=2, sticky="ew",padx=10, pady=5)

        self.dev_status = tk.Entry(self.root)
        self.dev_status.grid(column=0,row=2,columnspan=2,sticky="ew",padx=10, pady=5)
        self.dev_status.insert(tk.END,"未接続")

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.view_open()
    def dev_open(self):
        self.parent.baker.ser.close()
        self.dev_status.delete(0,tk.END)
        self.parent.debug_view.insert(tk.END, "接続完了\n")

        port = self.port_var.get()
        if not port:
            self.dev_status.insert(tk.END,"デバイス未選択")
            return

        self.parent.baker.ser.port = port
        self.parent.baker.ser.open()
        
        read_thread = threading.Thread(target=self.dev_connection, daemon=True)
        read_thread.start()

    def close(self):
        self.root.withdraw()
    def view_open(self):
        #シリアルポート情報の取得
        ports = serial.tools.list_ports.comports()
        port_names = [port.device for port in ports]
        self.port_var.set('')  # 初期値を空に設定
        self.port_menu["menu"].delete(0, tk.END)
        for port_name in port_names:
            self.port_menu["menu"].add_command(label=port_name, command=tk._setit(self.port_var, port_name))
            self.root.deiconify()
    def dev_connection(self):
        self.parent.progress_bar.config(mode="indeterminate")
        self.parent.progress_bar.start(10)
        self.dev_status.insert(tk.END,"接続中...")
        sleep(3)
        result = self.parent.baker.device_check()
        self.dev_status.delete(0,tk.END)
        self.dev_status.insert(tk.END,"接続完了 : "+result)
        self.parent.status_bar["text"] = "接続完了 : "+result
        self.parent.progress_bar.stop()
        self.parent.progress_bar.config(mode="determinate")
        self.parent.progress_bar["value"] = 0
        self.parent.progress_bar.update()


    def quit(self):
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    Main(root)
    root.mainloop()