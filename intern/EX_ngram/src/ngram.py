#-*-coding:utf-8

import codecs
import re
import operator
import os
import argparse
import sys

parser = argparse.ArgumentParser(description='ngram')
parser.add_argument('--filename', dest='filename', required=True, help='filename')
parser.add_argument('--dst', dest='dst', required=True, help='dst_dir')
args = parser.parse_args()


class Ngram:
	def ngram(self, text = "", n = 1):

		if len(text) < 1:
			return	dict()
		start_symbol = u'^ '
		end_symbol = u'$'

		di = dict()

		text = str(text).replace('[','').replace(']','').replace('(','').replace(')','')
		parse_text = re.sub('[-|=|.|..|...|....|#|/|?|:|}|,|\"|\'|▲|]','',text)
		parse_text = re.sub('\n', ' ', parse_text)


		word_list = parse_text.split(' ')

		for i in range(len(word_list)-1, (n-2) ,-1):
			temp_str = ""
			for j in range(n):
				temp_str += word_list[i - j]
				if j != n-1:
					temp_str += " "

			if di.get(temp_str):
				di[temp_str]=di[temp_str] + 1
			else:
				di[temp_str]=1

		return di

	def total_len(self, ngram_dict):
		temp = 0
		for i in ngram_dict.values():
			temp += i
		return temp




#######################################################


#linear interpolation
	def probability_unigram(self, ngram_dict):
		di = dict()

		total = self.total_len(ngram_dict)
		lamda0=0.2
		lamda1=0.8
		for key, value in ngram_dict.items():

			di.update({key: lamda1 * (float(value) / float(total)) + lamda0 })

		return di
#linear interpolation
	def probability_bigram(self, uni_dict, bi_dict):
		di = dict()
		lamda0=0.1
		lamda1=0.3
		lamda2=0.6
		total = self.total_len(uni_dict)

		for key, value in bi_dict.items():
			tmp = key.split(" ")
			tmp = str(tmp[0])

			uni_dict_value = 1.0
			if uni_dict.get(tmp) is not None:
				uni_dict_value = uni_dict.get(tmp)


			di.update({key : lamda2 * (float(value) / float(uni_dict_value)) + lamda1*(float(uni_dict_value) / float(total)) +lamda0})
		return di


#linear interpolation
	def probability_trigram(self, uni_dict, bi_dict, tri_dict):
		di = dict()
		total = self.total_len(uni_dict)
		lamda0=0.1
		lamda1=0.2
		lamda2=0.3
		lamda3=0.4

		for key, value in tri_dict.items():
			tmp = key.split(" ")
			uni_tmp = tmp[0] +" "
			tmp = str(tmp[0]) + " " + str(tmp[1]) + " "

			bi_dict_value = 1.0
			if bi_dict.get(tmp) is not None:
				bi_dict_value = bi_dict.get(tmp)

			uni_dict_value = 1.0
			if uni_dict.get(uni_tmp) is not None:
				uni_dict_value = uni_dict.get(uni_tmp)

			di.update({key : lamda3*(float(value) / float(bi_dict_value)) + lamda2*(float(bi_dict_value) / float(uni_dict_value)) + lamda1*(float(uni_dict_value) / float(total))+lamda0 })

		return di


def write_file(list, path, filename):
	if not os.path.exists(path):
		os.makedirs(path)

	read_file = open(path+'/'+filename+".txt", 'w')
	for item in list:
		read_file.write(str(item[0]))
		read_file.write(' ')
		read_file.write(str(item[1]))
		read_file.write('\n')
	print(filename + ".txt 파일을 생성하였습니다.")

def write_file_string(str_value, value, path, filename):
	if not os.path.exists(path):
		os.makedirs(path)


	read_file = open(path+'/'+filename+".txt", 'a')

	read_file.write(str_value)
	read_file.write(' ')
	read_file.write(str(value))
	read_file.write('\n')


def ngram_file_write(text, n):
	result_dic = n_gram.ngram(text, n )
	result_dic_sort = sorted(result_dic.items(), key=operator.itemgetter(1), reverse=True)

	file_name=""

	if n==1 :
		file_name = "unigram"
	elif n==2:
		file_name = "bigram"
	elif n==3:
		file_name = "trigram"

	write_file(result_dic_sort, dst, file_name)
	return result_dic

if __name__=="__main__":
	filename = args.filename
	dst = args.dst

	n_gram = Ngram()

	f = open(filename+'.txt', 'r')
	text = f.read()

	uni_result = ngram_file_write(text, 1)
	bi_result = ngram_file_write(text, 2)
	tri_result = ngram_file_write(text, 3)

	uni_probability = n_gram.probability_unigram(uni_result)
	uni_probability_sort = sorted(uni_probability.items(), key=operator.itemgetter(1), reverse = True)
	write_file(uni_probability_sort, dst, "unigram_probability")

	bi_probability = n_gram.probability_bigram(uni_result , bi_result)
	bi_probability_sort = sorted(bi_probability.items(), key=operator.itemgetter(1), reverse = True)
	write_file(bi_probability_sort,dst, "bigram_probability")

	tri_probability = n_gram.probability_trigram(uni_result, bi_result, tri_result)
	tri_probability_sort = sorted(tri_probability.items(), key=operator.itemgetter(1), reverse = True)
	write_file(tri_probability_sort, dst, "trigram_probability")



	f.close()
