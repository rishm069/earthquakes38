#Conversion is performed in accordance  with http://seis-bykl.ru/modules.php?name=Popul_f
def klass_conversion(K):
	if K > 14:
		#K=8+1.1M
		M = (K - 8)/1.1
		return round(M, 1)
	if K <= 14:
		#K=4+1.8M
		M = (K - 4)/1.8
		return round(M, 1)