# stock_notifier

Overview
-	`stock_notifier` is a small collection of scripts for fetching and analysing stock market data. It includes simple crawlers, indicator scripts and example tools to collect CSV market data and run quick experiments.
-	The project can integrate with a LINE bot to push a formatted table (image) of recent market data to your LINE account.


Key Features
-	Fetch and export market data (CSV)
-	Basic technical indicators and data analysis scripts
-	Can serve as a data source for automated alerts or further backtesting

Project Structure (high-level)
-	`crawler.py`: main crawler / data collection script
-	`lineV3.py`: alternative data processing / analysis example
-	`market_data.csv`: sample or exported market data
-	`crawl/`: multiple analysis and helper modules (e.g. choice.py, PCR.py, volume.py)
-	`test/`: experimental or test scripts

-	Python 3.8+
-	Install dependencies:

Additional configuration
-	To enable LINE notifications, set the following environment variables with your own credentials before running the scripts:

```
export LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
export LINE_USER_ID=your_line_user_id
```

On Windows PowerShell, use:

```powershell
$env:LINE_CHANNEL_ACCESS_TOKEN = "your_channel_access_token"
$env:LINE_USER_ID = "your_line_user_id"
```

Note: the code expects these values in the environment as `LINE_CHANNEL_ACCESS_TOKEN` and `LINE_USER_ID`.

```bash
pip install -r requirements.txt
```

Quick Start
1. Clone or download the repository to your machine.
2. Change into the project directory and install dependencies:

```bash
cd path/to/stock
pip install -r requirements.txt
```

3. Run example scripts (choose as needed):

```bash
python crawler.py
```

Notes
-	`market_data.csv` may contain sample or exported historical data — back it up if needed.
-	Scripts inside `crawl/` are generally independent and can be used as modules or executed individually.

Contributing
-	Contributions are welcome via pull requests. Please ensure dependencies and basic functionality work before submitting.

Contact
-	If you encounter issues or need help, open an issue in the repository or contact the maintainer.
