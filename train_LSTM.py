'''
  code by Tae Hwan Jung(Jeff Jung) @graykode
  Reference : https://github.com/prakashpandey9/Text-Classification-Pytorch/blob/master/models/LSTM_Attn.py
'''
import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]="0"

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import torch.nn.functional as F
import matplotlib.pyplot as plt

from models.networks.biLSTM_attention import BiLSTM_Attention
from datahub.dataset.crypto_dataloader import CryptoCurrencyPriceDataset
from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
dtype = torch.FloatTensor

# Bi-LSTM(Attention) Parameters
embedding_dim = 6
n_hidden = 128 # number of hidden units in one cell
num_classes = 4  # 0 or 1

# 3 words sentences (=sequence_length is 3)
# sentences = ["i love you", "he loves me", "she likes baseball", "i hate you", "sorry for that", "this is awful"]
# labels = [1, 1, 1, 0, 0, 0]  # 1 is good, 0 is not good.

# word_list = " ".join(sentences).split()
# word_list = list(set(word_list))
# word_dict = {w: i for i, w in enumerate(word_list)}
# vocab_size = len(word_dict)

# inputs = []
# for sen in sentences:
#     inputs.append(np.asarray([word_dict[n] for n in sen.split()]))

# targets = []
# for out in labels:
#     targets.append(out) # To using Torch Softmax Loss function

# input_batch = Variable(torch.LongTensor(inputs))
# target_batch = Variable(torch.LongTensor(targets))

binance_crypto_data_crawler = BinanceCryptoDataCrawler()
binance_crypto_data_crawler.load_from_file(r'dataset/binance_crypto_price_data.json')

train_loader = torch.utils.data.DataLoader(CryptoCurrencyPriceDataset(binance_crypto_data_crawler, mode='train'), batch_size=4,
                                          shuffle=False)
val_loader = torch.utils.data.DataLoader(CryptoCurrencyPriceDataset(binance_crypto_data_crawler, mode='val'), batch_size=4,
                                          shuffle=False)
test_loader = torch.utils.data.DataLoader(CryptoCurrencyPriceDataset(binance_crypto_data_crawler, mode='test'), batch_size=4,
                                          shuffle=False)

model = BiLSTM_Attention(embedding_dim, n_hidden, num_classes)

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

import pdb; pdb.set_trace()
# Training

loss_eval = 100000
for epoch in range(200):
    optimizer.zero_grad()

    losses = []
    for batch in train_loader:
        input_batch = batch[0]
        target_batch = batch[1]

        output, attention = model(input_batch)
        loss = criterion(output, target_batch)
        
        losses.append(loss)
        # if (epoch + 1) % 100 == 0:
        loss.backward()
        optimizer.step()
    
    if epoch % 5 == 0:
        model.eval()

        val_losses = []
        for batch in val_loader:
            input_batch = batch[0]
            target_batch = batch[1]

            output, attention = model(input_batch)
            loss = criterion(output, target_batch)

            val_losses += loss
        
        if sum(val_losses) / len(val_losses) < loss_eval:
            loss_eval = sum(val_losses) / len(val_losses) 
            torch.save(model.state_dict(), 'weights/BiLSTM_Best.pth')

    print('Epoch:', '%04d' % (epoch + 1), 'cost =', '{:.6f}'.format(sum(losses) / len(losses)))


# # Test
# test_text = 'sorry hate you'
# tests = [np.asarray([word_dict[n] for n in test_text.split()])]
# test_batch = Variable(torch.LongTensor(tests))

# # Predict
# predict, _ = model(test_batch)
# predict = predict.data.max(1, keepdim=True)[1]
# if predict[0][0] == 0:
#     print(test_text,"is Bad Mean...")
# else:
#     print(test_text,"is Good Mean!!")
    
# fig = plt.figure(figsize=(6, 3)) # [batch_size, n_step]
# ax = fig.add_subplot(1, 1, 1)
# ax.matshow(attention, cmap='viridis')
# ax.set_xticklabels(['']+['first_word', 'second_word', 'third_word'], fontdict={'fontsize': 14}, rotation=90)
# ax.set_yticklabels(['']+['batch_1', 'batch_2', 'batch_3', 'batch_4', 'batch_5', 'batch_6'], fontdict={'fontsize': 14})
# plt.show()