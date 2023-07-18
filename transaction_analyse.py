import json

def main():
    transaction_histore_file = r'all_transaction_history.json'

    with open(transaction_histore_file, 'r') as f:
        transaction_history = json.load(f)
    
    time_frame = ['4h', '1d', '1w']

    symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 
        'SOLUSDT', 'DOTUSDT', 'BCHUSDT', 
        'LTCUSDT', 'XRPUSDT', 'AVAXUSDT'
    ]

    pattern_statistics = {}

    for pattern, transactions in transaction_history.items():
        pattern_statistics[pattern] = {}
        for tf in time_frame:
            pattern_statistics[pattern][tf] = {}
            for symbol in symbols:
                total_win_trade = len([t for t in transactions if t['symbol'] == symbol and t['time_frame'] == tf and t['win_or_lose'] == "win"])
                total_trade = len([t for t in transactions if t['symbol'] == symbol and t['time_frame'] == tf])
                win_rate = total_win_trade / total_trade if total_trade > 0 else 0

                if win_rate < 0.4 or total_trade < 3:
                    continue
                pattern_statistics[pattern][tf][symbol] = {
                    "total_win_trade": total_win_trade,
                    "total_trade": total_trade,
                    "win_rate": win_rate
                }
            
            # Sort by win rate
            pattern_statistics[pattern][tf] = dict(sorted(pattern_statistics[pattern][tf].items(), key=lambda item: item[1]['win_rate'], reverse=True))

        # Print result
        print("Pattern: ", pattern)
        for tf in time_frame:
            print("Time frame: ", tf)
            for symbol, stat in pattern_statistics[pattern][tf].items():
                print(symbol, ": ", stat)
            print("")
    
if __name__ == '__main__':
    main()