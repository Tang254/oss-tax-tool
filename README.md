# OSS Tax Tool

## English

This project provides a small tool for calculating:

- cross-border OSS VAT totals
- selected domestic EU VAT totals

The tool combines:

- JTL/Wawi invoice exports
- Amazon VAT transaction exports

### Privacy and Data Safety

Do not upload or share raw exports from Amazon, JTL, or Wawi.

Those files may contain:

- customer names and addresses
- order numbers
- VAT identifiers
- invoice download links
- other commercially sensitive transaction data

Only share:

- code
- documentation
- fully anonymized sample files

### Requirements

- Python 3.10+
- `pandas`

Install dependencies:

```bash
pip install -r requirements.txt
```

### Usage

#### 1. Cross-border OSS totals

```bash
python oss_tax_tool.py --mode oss --jtl-file path/to/JTL-Export.csv --amazon-file path/to/Amazon-Export.csv
```

#### 2. Domestic EU VAT totals

Default countries: `FR IT PL CZ ES`

```bash
python oss_tax_tool.py --mode domestic --jtl-file path/to/JTL-Export.csv --amazon-file path/to/Amazon-Export.csv
```

You can override the domestic countries:

```bash
python oss_tax_tool.py --mode domestic --jtl-file path/to/JTL-Export.csv --amazon-file path/to/Amazon-Export.csv --countries FR IT ES
```

#### 3. Write output to a chosen file

```bash
python oss_tax_tool.py --mode oss --jtl-file path/to/JTL-Export.csv --amazon-file path/to/Amazon-Export.csv --output results.csv
```

If `--output` is omitted, the tool writes a timestamped CSV in the current directory.

### Desktop GUI for non-technical users

The project also includes a Tkinter desktop interface:

```bash
python oss_tax_tool_gui.py
```

The GUI allows a user to:

- choose the JTL CSV with a file picker
- choose the Amazon CSV with a file picker
- choose `oss` or `domestic` mode
- choose an output folder
- preview the result before opening the saved CSV

This is the recommended option for users who do not want to work in VS Code or the command line.

### Build a Windows EXE with PyInstaller

Install PyInstaller:

```bash
pip install pyinstaller
```

Then build the desktop app:

```bash
build_windows.bat
```

Or run PyInstaller directly:

```bash
python -m PyInstaller --noconfirm --onefile --windowed --name OSS-Tax-Tool oss_tax_tool_gui.py
```

If the build succeeds, the EXE will be created in the `dist` folder.

### Expected Input Files

#### JTL export

The script expects a semicolon-separated CSV in a common JTL export format and uses columns such as:

- `LA Land ISO`
- `Versandland Länder ISO`
- `Auftragswährung`
- `Gesamtbetrag Netto (alle Ust.)`
- `Betrag USt. (2 Nachkommastellen)`
- `USt.frei`

The script also handles some mojibake variants of German column names.

#### Amazon export

The script expects the Amazon VAT transaction export with columns such as:

- `TRANSACTION_TYPE`
- `SALE_DEPART_COUNTRY`
- `SALE_ARRIVAL_COUNTRY`
- `TOTAL_ACTIVITY_VALUE_AMT_VAT_EXCL`
- `TOTAL_ACTIVITY_VALUE_VAT_AMT`
- `PRICE_OF_ITEMS_VAT_RATE_PERCENT`

### Data Handling Recommendations

Recommended workflow:

1. Keep code and documentation separate from real export data.
2. Store real exports in a local folder that is not shared publicly.
3. Run the script by passing local file paths as arguments.

### Limitations

- The logic reflects a specific workflow and export structure.
- VAT handling in `domestic` mode intentionally follows the original scripts.
- You should validate the output against your accounting and filing process before submitting tax reports.

---

## 中文说明

这个项目提供一个用于计算以下数据的小工具：

- 跨境 OSS 增值税汇总
- 部分欧盟国家的本地增值税汇总

它会结合两类导出数据：

- JTL/Wawi 发票导出
- Amazon VAT 交易流水导出

### 隐私与数据安全

不要上传、共享或公开 Amazon、JTL 或 Wawi 的原始导出文件。

这些文件通常包含：

- 客户姓名和地址
- 订单号
- VAT 税号
- 发票下载链接
- 其他商业敏感交易信息

适合共享的内容通常只有：

- 代码
- 文档
- 已彻底脱敏的示例文件

### 环境要求

- Python 3.10+
- `pandas`

安装依赖：

```bash
pip install -r requirements.txt
```

### 用法

#### 1. 计算跨境 OSS

```bash
python oss_tax_tool.py --mode oss --jtl-file path/to/JTL-Export.csv --amazon-file path/to/Amazon-Export.csv
```

#### 2. 计算本地欧盟增值税

默认国家：`FR IT PL CZ ES`

```bash
python oss_tax_tool.py --mode domestic --jtl-file path/to/JTL-Export.csv --amazon-file path/to/Amazon-Export.csv
```

也可以手动指定国家：

```bash
python oss_tax_tool.py --mode domestic --jtl-file path/to/JTL-Export.csv --amazon-file path/to/Amazon-Export.csv --countries FR IT ES
```

#### 3. 指定输出文件

```bash
python oss_tax_tool.py --mode oss --jtl-file path/to/JTL-Export.csv --amazon-file path/to/Amazon-Export.csv --output results.csv
```

如果不传 `--output`，脚本会在当前目录自动生成带时间戳的结果文件。

### 给非技术用户的桌面图形界面

项目中还包含一个 Tkinter 图形界面版本：

```bash
python oss_tax_tool_gui.py
```

图形界面支持：

- 点击选择 JTL CSV
- 点击选择 Amazon CSV
- 选择 `oss` 或 `domestic` 模式
- 选择输出目录
- 预览结果并保存 CSV

如果使用者不会 VS Code 或命令行，这会是更合适的使用方式。

### 使用 PyInstaller 打包 Windows EXE

先安装 PyInstaller：

```bash
pip install pyinstaller
```

然后执行：

```bash
build_windows.bat
```

或者直接运行：

```bash
python -m PyInstaller --noconfirm --onefile --windowed --name OSS-Tax-Tool oss_tax_tool_gui.py
```

如果打包成功，生成的 `.exe` 会出现在 `dist` 目录下。

### 输入文件要求

#### JTL 导出

脚本预期读取的是常见 JTL 格式的分号分隔 CSV，依赖的列包括：

- `LA Land ISO`
- `Versandland Länder ISO`
- `Auftragswährung`
- `Gesamtbetrag Netto (alle Ust.)`
- `Betrag USt. (2 Nachkommastellen)`
- `USt.frei`

同时也兼容部分德语列名乱码形式。

#### Amazon 导出

脚本预期读取 Amazon VAT transaction export，依赖的列包括：

- `TRANSACTION_TYPE`
- `SALE_DEPART_COUNTRY`
- `SALE_ARRIVAL_COUNTRY`
- `TOTAL_ACTIVITY_VALUE_AMT_VAT_EXCL`
- `TOTAL_ACTIVITY_VALUE_VAT_AMT`
- `PRICE_OF_ITEMS_VAT_RATE_PERCENT`

### 数据使用建议

建议这样使用：

1. 将代码和文档与真实导出数据分开存放。
2. 真实导出数据保存在不会被公开共享的本地目录中。
3. 运行脚本时，通过参数传入本地真实文件路径。

### 限制说明

- 当前逻辑基于现有业务流程和导出格式整理而来。
- `domestic` 模式下的国家与税率逻辑保持了原脚本的思路。
- 在正式申报前，仍建议和你的财税流程做一次人工复核。
