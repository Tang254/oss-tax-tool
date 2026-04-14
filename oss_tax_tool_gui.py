from pathlib import Path
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import pandas as pd

from oss_tax_tool import DOMESTIC_VAT_COUNTRIES, run_calculation


class TaxToolApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OSS Tax Tool")
        self.root.geometry("860x700")
        self.root.minsize(760, 620)

        self.mode_var = tk.StringVar(value="oss")
        self.jtl_file_var = tk.StringVar()
        self.amazon_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.cwd()))
        self.countries_var = tk.StringVar(value="FR IT PL CZ ES")
        self.status_var = tk.StringVar(value="Select files and run a calculation.")

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(5, weight=1)

        ttk.Label(
            container,
            text="OSS Tax Tool",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        ttk.Label(
            container,
            text="Pick the export files, choose a mode, and save the result CSV without using the command line.",
            wraplength=760,
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 14))

        mode_frame = ttk.LabelFrame(container, text="Mode", padding=12)
        mode_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        ttk.Radiobutton(mode_frame, text="Cross-border OSS", variable=self.mode_var, value="oss").pack(
            side="left", padx=(0, 16)
        )
        ttk.Radiobutton(mode_frame, text="Domestic EU VAT", variable=self.mode_var, value="domestic").pack(
            side="left"
        )

        self._add_file_row(container, 3, "JTL CSV", self.jtl_file_var, self._browse_jtl_file)
        self._add_file_row(container, 4, "Amazon CSV", self.amazon_file_var, self._browse_amazon_file)
        self._add_file_row(container, 5, "Output Folder", self.output_dir_var, self._browse_output_dir)

        options_frame = ttk.LabelFrame(container, text="Domestic Mode Options", padding=12)
        options_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        options_frame.columnconfigure(1, weight=1)
        ttk.Label(
            options_frame,
            text="Countries (space-separated ISO codes)",
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(options_frame, textvariable=self.countries_var).grid(row=0, column=1, sticky="ew")
        ttk.Label(
            options_frame,
            text=f"Default domestic countries: {' '.join(DOMESTIC_VAT_COUNTRIES.keys())}",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        button_frame = ttk.Frame(container)
        button_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        ttk.Button(button_frame, text="Run Calculation", command=self.run).pack(side="left")
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder).pack(
            side="left", padx=(10, 0)
        )

        status_frame = ttk.LabelFrame(container, text="Status", padding=12)
        status_frame.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        ttk.Label(status_frame, textvariable=self.status_var, wraplength=760).pack(anchor="w")

        preview_frame = ttk.LabelFrame(container, text="Preview", padding=12)
        preview_frame.grid(row=9, column=0, columnspan=3, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.preview = scrolledtext.ScrolledText(preview_frame, wrap="none", font=("Consolas", 10))
        self.preview.grid(row=0, column=0, sticky="nsew")
        self.preview.insert("1.0", "No results yet.")
        self.preview.configure(state="disabled")

    def _add_file_row(self, parent: ttk.Frame, row: int, label: str, variable: tk.StringVar, command) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=(0, 10))
        ttk.Button(parent, text="Browse", command=command).grid(row=row, column=2, sticky="ew", pady=(0, 10))

    def _browse_jtl_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select JTL CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.jtl_file_var.set(path)

    def _browse_amazon_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Amazon CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.amazon_file_var.set(path)

    def _browse_output_dir(self) -> None:
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_dir_var.set(path)

    def _set_preview_text(self, text: str) -> None:
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", text)
        self.preview.configure(state="disabled")

    def _build_output_path(self) -> str:
        output_dir = Path(self.output_dir_var.get().strip() or Path.cwd())
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        return str(output_dir / f"{self.mode_var.get()}_results_{timestamp}.csv")

    def open_output_folder(self) -> None:
        output_dir = Path(self.output_dir_var.get().strip() or Path.cwd())
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(output_dir.resolve())  # type: ignore[attr-defined]
        except Exception:
            messagebox.showinfo("Output Folder", f"Output folder:\n{output_dir}")

    def run(self) -> None:
        jtl_file = self.jtl_file_var.get().strip()
        amazon_file = self.amazon_file_var.get().strip()
        output_dir = self.output_dir_var.get().strip()

        if not jtl_file or not amazon_file:
            messagebox.showerror("Missing File", "Please select both the JTL CSV and the Amazon CSV.")
            return

        if not Path(jtl_file).exists():
            messagebox.showerror("JTL File Not Found", f"File not found:\n{jtl_file}")
            return

        if not Path(amazon_file).exists():
            messagebox.showerror("Amazon File Not Found", f"File not found:\n{amazon_file}")
            return

        if not output_dir:
            messagebox.showerror("Missing Output Folder", "Please choose an output folder.")
            return

        countries = self.countries_var.get().strip().split()

        try:
            self.status_var.set("Running calculation...")
            self.root.update_idletasks()

            result_df, output_path = run_calculation(
                mode=self.mode_var.get(),
                jtl_file=jtl_file,
                amazon_file=amazon_file,
                output=self._build_output_path(),
                countries=countries,
            )
            self._set_preview_text(result_df.to_string(index=False))
            self.status_var.set(f"Finished successfully. Result saved to: {output_path}")
            messagebox.showinfo("Done", f"Calculation finished.\n\nSaved result to:\n{output_path}")
        except Exception as exc:
            self.status_var.set("Calculation failed.")
            self._set_preview_text("")
            messagebox.showerror("Calculation Failed", str(exc))


def main() -> None:
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    app = TaxToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
