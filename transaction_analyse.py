import json

def main():
    transaction_histore_file = r'dataset/crypto_all_transaction_history.json'

    with open(transaction_histore_file, 'r') as f:
        transaction_history = json.load(f)
    
    time_frame = ['4h', '1d', '1w']

    symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 
        'SOLUSDT', 'BCHUSDT', 'ATOMUSDT', 
        'LTCUSDT', 'AVAXUSDT', 'UNIUSDT'
    ]

    symbols = ['ADAUSDT']

    pattern_statistics = {}

    for pattern, transactions in transaction_history.items():
        pattern_statistics[pattern] = {}
        for tf in time_frame:
            pattern_statistics[pattern][tf] = {}
            for symbol in symbols:
                # Use rsi to filter
                low_limit_rsi = 50
                high_limit_ris = 40

                total_win_trade = len([t for t in transactions if t['symbol'] == symbol and t['time_frame'] == tf and t['win_or_lose'] == "win"])
                total_lose_trade = len([t for t in transactions if t['symbol'] == symbol and t['time_frame'] == tf and t['win_or_lose'] == "lose"])
                total_trade = total_win_trade + total_lose_trade
                win_rate = total_win_trade / total_trade if total_trade > 0 else 0

                if win_rate < 0.4 or total_trade < 3:
                    continue
                pattern_statistics[pattern][tf][symbol] = {
                    "total_win_trade": total_win_trade,
                    "total_lose_trade": total_lose_trade,
                    "total_trade": total_trade,
                    "win_rate": win_rate
                }
            
            # Sort by win rate
            pattern_statistics[pattern][tf] = dict(sorted(pattern_statistics[pattern][tf].items(), key=lambda item: item[1]['win_rate'], reverse=True))

        if not "strong_bull" in pattern:
            continue
        
        # Print result
        print("Pattern: ", pattern)
        for tf in time_frame:
            print("Time frame: ", tf)
            for symbol, stat in pattern_statistics[pattern][tf].items():
                print(symbol, ": ", stat)
    
if __name__ == '__main__':
    main()