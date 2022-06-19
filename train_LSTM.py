'''
  code by Tae Hwan Jung(Jeff Jung) @graykode
  Reference : https://github.com/prakashpandey9/Text-Classification-Pytorch/blob/master/models/LSTM_Attn.py
'''
import os
# os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
# os.environ["CUDA_VISIBLE_DEVICES"]="0"

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import torch.nn.functional as F
import matplotlib.pyplot as plt

from models.networks.biLSTM_attention import BiLSTM_Attention
from datahub.dataset.crypto_dataloader import CryptoCurrencyPriceDataset
from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler

import argparse

def parameter_parser():
	parser = argparse.ArgumentParser(description = "Crypto Price Prediction")

	parser.add_argument("--epochs",
							dest = "epochs",
							type = int,
							default = 300,
						help = "Number of gradient descent iterations. Default is 200.")

	parser.add_argument("--learning_rate",
							dest = "learning_rate",
							type = float,
							default = 0.001,
						help = "Gradient descent learning rate. Default is 0.01.")

	parser.add_argument("--hidden_dim",
							dest = "hidden_dim",
							type = int,
							default = 128,
						help = "Number of neurons by hidden layer. Default is 128.")
	
	parser.add_argument("--window_len",
							dest = "window_len",
							type = int,
							default = 128,
						help = "Length of input")
						
	parser.add_argument("--lstm_layers",
							dest = "lstm_layers",
							type = int,
							default = 1,
					help = "Number of LSTM layers")
					
	parser.add_argument("--batch_size",
								dest = "batch_size",
								type = int,
								default = 64,
							help = "Batch size")

	parser.add_argument("--num_class",
							dest = "num_class",
							type = int,
							default = 4,
						help = "Number of class. Defaut 4: high, open, close, low")	
                        			 
	return parser.parse_args()

def weights_init_uniform(m):
	classname = m.__class__.__name__
	# for every Linear layer in a model..
	if classname.find('Linear') != -1:
		# apply a uniform distribution to the weights and a bias=0
		m.weight.data.uniform_(0.0, 1.0)
		m.bias.data.fill_(0)

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

if __name__ == "__main__":
	args = parameter_parser()

	# Bi-LSTM(Attention) Parameters
	embedding_dim = 6

	binance_crypto_data_crawler = BinanceCryptoDataCrawler()
	binance_crypto_data_crawler.load_from_file(r'dataset/btc_binance_crypto_price_data.json')

	if torch.cuda.is_available():
		device = torch.device('cuda')
	else:
		device = torch.device('cpu')

	train_loader = torch.utils.data.DataLoader(CryptoCurrencyPriceDataset(binance_crypto_data_crawler, mode='train', window_len=args.window_len), batch_size=args.batch_size,
											shuffle=False)
	val_loader = torch.utils.data.DataLoader(CryptoCurrencyPriceDataset(binance_crypto_data_crawler, mode='val', window_len=args.window_len), batch_size=args.batch_size,
											shuffle=False)
	test_loader = torch.utils.data.DataLoader(CryptoCurrencyPriceDataset(binance_crypto_data_crawler, mode='test', window_len=args.window_len), batch_size=args.batch_size,
											shuffle=False)

	model = BiLSTM_Attention(embedding_dim, args.hidden_dim, args.num_class, device).to(device)
	model.apply(weights_init_uniform)

	log_file = open(f'weights/BiLSTM_Best_wl{args.window_len}_hds{args.hidden_dim}_bs{args.batch_size}_lr{args.learning_rate}.log', 'w')

	print(f"Parameters: {count_parameters(model)}")
	log_file.write(f"Parameters: {count_parameters(model)}\n")

	criterion = nn.MSELoss()
	optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

	# Training

	loss_eval = 100000
	best_acc = -1

	for epoch in tqdm(range(args.epochs)):
		model.train()
		optimizer.zero_grad()
		losses = []
		for idx, batch in tqdm(enumerate(train_loader)):
			input_batch = batch[0].to(device)
			target_batch = batch[1].to(device)

			output, attention = model(input_batch)
			loss = criterion(output, target_batch)
			
			losses.append(loss)

			loss.backward()
			optimizer.step()
		print('Epoch:', '%04d' % (epoch + 1), '. Train loss =', '{:.6f}'.format(sum(losses) / len(losses)))
		log_file.write('Epoch: ' + '%04d' % (epoch + 1) + '. Train loss =' + '{:.6f}'.format(sum(losses) / len(losses)) + "\n")

		if epoch % 1 == 0:
			model.eval()

			val_losses = []
			with torch.no_grad():
				pred = np.array([])
				gt = np.array([])

				for batch in val_loader:
					input_batch = batch[0].to(device)
					target_batch = batch[1].to(device)

					output, attention = model(input_batch)
					loss = criterion(output, target_batch)

					pred = np.append(pred, np.array([int(o[3]>=o[0]) for o in output.cpu().numpy()]))
					gt = np.append(gt, np.array([int(o[3]>=o[0]) for o in target_batch.cpu().numpy()]))

					val_losses.append(loss)
				
				accuracy = (len(pred) - sum(np.add(pred, gt) % 2)) / len(pred)
				print('\tVal loss =', '{:.6f}'.format(sum(losses) / len(losses)))
				log_file.write('\tVal loss =' + '{:.6f}'.format(sum(losses) / len(losses)) + f". Accuracy: {accuracy}." + "\n")

				if sum(val_losses) / len(val_losses) < loss_eval and accuracy >= best_acc:
					print("\t\tFound best checkpoint -> Saving..")
					log_file.write("\tFound best checkpoint -> Saving..\n")
					loss_eval = sum(val_losses) / len(val_losses)
					torch.save(model.state_dict(), f'weights/BiLSTM_Best_wl{args.window_len}_hds{args.hidden_dim}_bs{args.batch_size}_lr{args.learning_rate}.pth')
				
				
