#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Programa scanner em python
# Para o sniffer usamos a biblioteca Pcapy, que é feita especialmente para isso
# Versão python usada: python 2.7
# A opção sniffer só captura pacotes TCP, UDP, e ICMP

import getpass #biblioteca que permite a leitura de senhas sem aparecer na tela
import smtplib as s #biblioteca usada no spam de emails
from urllib2 import urlopen #biblioteca usada para descobrir o ip externo
from xml.dom import minidom as dom #biblioteca usada também para descobrir o ip externo
import socket
from struct import *
import datetime
import pcapy #biblioteca usada para o sniffer de rede
import sys
from os import system #biblioteca usada para algumas funções do programa
from scapy.all import * #biblioteca base do programa

def help():
   print """
   ==============================================================================================================================================
   =		Scanner de rede em Python                                                                                                       =
   ==============================================================================================================================================
   =            by: Túlio Marcos & Amanda Moulins                                                                                               =
   ==============================================================================================================================================
   = Opções:                                                                                                                                    =
   = 1 -> Utilizar o traceroute da scapy                                                                                                        =  
   =                                                                                                                                            =
   = 2 -> Ver o IP do link de internet                                                                                                          =
   =                                                                                                                                            =
   = 3 -> Descobrir o sistema operacional através do IP                                                                                         =
   =                                                                                                                                            =
   = 4 -> Utilizar o ping                                                                                                                       =
   =                                                                                                                                            =
   = 5 -> Sniffar a rede                                                                                                                        =
   =                                                                                                                                            =
   = 6 -> Usar o spam de email                                                                                                                  =
   =                                                                                                                                            =
   = 7 -> Se tornar o maior Hacker de todos os tempos                                                                                           =
   ==============================================================================================================================================
   """
system('clear')
help()
opcao = raw_input("Escolha uma opção: ")
if opcao == "1": #traceroute da scapy
   alvo = raw_input("IP destino: ") #ip do destino
   ttl=1 #tempo de vida do pacote deve iniciar em 1
   while 1:
     p=sr1(IP(dst=alvo, ttl=ttl)/ICMP(id=os.getpid()), verbose=0) #criando o pacote para ser enviado
     if p[ICMP].type == 11 and p[ICMP].code == 0:
	print ttl, '->', p.src
	ttl += 1
     elif p[ICMP].type == 0:
	print ttl, '->', p.src
	break
#traceroute da scapy termina aqui
elif opcao == "2": #descobrir o ip externo
   url = dom.parseString(urlopen('http://www.speedtest.net/speedtest-config.php').read()) #entra no site e o lê
   client = url.getElementsByTagName('client') #pega a informação que está no campo 'client' e coloca na variavel
   print(client[0].attributes['ip'].value)
elif opcao == "3": #descobrir o SO pelo tempo de vida do pacote
   alvo = raw_input("IP destino: ")
   ip = IP() #pega o ip pela scapy
   ping = ICMP()
   ip.dst = alvo
   resp = sr1(ip/ping) #aqui cria o pacote
   res = sr1(ARP(pdst=alvo))
   if resp.ttl < 65:
      print """
   ==============================================================================================================================================
   =							Sistema Operacional: Linux                                                              =
   ==============================================================================================================================================
   """
   elif resp.ttl == 128:
      print """
   ==============================================================================================================================================
   =							Sistema Operacional: Windows                                                            =
   ==============================================================================================================================================
   """
elif opcao == "4":
   alvo = raw_input("IP destino: ")
   quantidade = raw_input("Quantidade: ")
   system('ping -c '+quantidade+ ' '+alvo)
elif opcao == "5": #sniffer de pacotes
   def main(argv):
      devices = pcapy.findalldevs()
      print devices
      print "Dispositivos disponiveis: "
      for d in devices:
        print d
      dev = raw_input("Insira o nome do dispositivo que deseja sniffar: ")
      print "Sniffando o dispositivo " + dev
      cap = pcapy.open_live(dev , 65536 , 1 , 0)
      while(1):
        #quando eu coloco isso tudo dentro da função "main" ele não mostra nada na tela quando seleciono essa opção
         (header, packet) = cap.next()
         parse_packet(packet) #DANDO ERRO (não ta conseguindo chamar a função)
   def eth_addr (a):
      b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
      return b
   def parse_packet (packet):
      eth_length = 14
      eth_header = packet[:eth_length]
      eth = unpack('!6s6sH' , eth_header)
      eth_protocol = socket.ntohs(eth[2])
      print 'MAC destino: ' + eth_addr(packet[0:6]) + ' MAC fonte: ' + eth_addr(packet[6:12]) + ' Protocolo: ' + str(eth_protocol)
      if eth_protocol == 8:
	ip_header = packet[eth_length:20+eth_length]
        iph = unpack('!BBHHHBBH4s4s' , ip_header)
	version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        iph_length = ihl * 4
	ttl = iph[5]
	protocol = iph[6]
	s_addr = socket.inet_ntoa(iph[8]);
	d_addr = socket.inet_ntoa(iph[9]);
	print 'Versão: ' + str(version) + ' Tamanho do cabeçalho do IP: ' + str(ihl) + ' TTL: ' + str(ttl) + ' Protocolo: ' + str(protocol) + ' IP fonte: ' + str(s_addr) + ' IP destino: ' + str(d_addr)
	if protocol == 6:
	   t = iph_length + eth_length
	   tcp_header = packet[t:t+20]
	   tcph = unpack('!HHLLBBHHH' , tcp_header)
	   source_port = tcph[0]
	   dest_port = tcph[1]
	   sequence = tcph[2]
	   acknowledgement = tcph[3]
	   doff_reserved = tcph[4]
	   tcph_length = doff_reserved >> 4
	   print 'Porta fonte: ' +str(source_port) + ' Porta destino: ' + str(dest_port) + ' Número da sequência: ' + str(sequence) + ' Reconhecimento: ' + str(acknowledgement) + ' Tamanho cabeçalho TCP: ' + str(tcph_length)
	   h_size = eth_length + iph_length + tcph_length * 4
	   data_size = len(packet) - h_size
	   data = packet[h_size:]
	   print 'Dados: ' + data
	elif protocol == 1:
	   u = iph_lenght + eth_length
	   icmph_length = 4
	   icmp_header = packet[u:u+4]
	   icmph = unpack('!BBH' , icmp_header)
	   icmp_type = icmph[0]
	   code = icmph[1]
	   checksum = icmph[2]
	   print 'Tipo: ' + str(icmp_type) + ' Código: ' + str(code) + ' Soma de verificação: ' + str(checksum)
	   h_size = eth_length + iph_length + icmph_length
	   data_size = len(packet) - h_size
	   data = packet[h_size:]
	   print 'Dados: ' + data
	elif protocol == 17:
	   u = iph_length + eth_length
	   udph_length = 8
	   udp_header = packet[u:u+8]
	   udph = unpack('!HHHH' , udp_header)
	   source_port = udph[0]
	   dest_port = udph[1]
	   length = udph[2]
	   checksum = udph[3]
	   print 'Porta fonte: ' + str(source_port) + ' Porta destino ' + str(dest_port) + ' Tamanho: ' + str(length) + ' Soma de verificação: ' + str(checksum)
	   h_size = eth_length + iph_length + udph_length
	   data_size = len(packet) - h_size
	   data = packet[h_size:]
	   print 'Dados: ' + data
	else:
	   print 'Nenhum pacote TCP/UDP/ICMP encontrado. '
   if __name__ == "__main__":
     main(sys.argv)
elif opcao == "6": #spam de email
   print "Logue com sua conta do Gmail para continuar, para usar esse script você terá de ativar o acesso a aplicativos menos seguros do email que vai enviar. (https://goo.gl/sLg7TS). \n"
   usuario = raw_input('Usuário: ')
   senha = getpass.getpass('Senha: ') #com essa opção a senha nao aparece na tela quando está sendo digitada
   obj = s.SMTP("smtp.gmail.com:587")
   obj.starttls()
   obj.login(usuario, senha)
   print "========================================================================"
   vitima = raw_input("Email da vítima: ")
   mensagem = raw_input("Mensagem: ")
   quantidade = int(raw_input("Quantidade: "))
   enviado = 0
   emailMensagem = ("---------------------------------------------------------------\n\r %s \n\r--------------------------------------------------------" % (mensagem))
   print "======================================================================="
   while enviado<quantidade:
      enviado = enviado+1
      obj.sendmail(usuario, vitima, emailMensagem)
      print "Enviando emails, " + str(enviado) + " emails enviados, pressione Ctrl + C para parar."
   print "======================================================================="
   print str(enviado) + " emails enviados. \n"
elif opcao == "7": #se tornar o maior hacker de todos os tempos uehueheuhe
   system('sudo apt-get install hollywood')
   system('hollywood')
else:
   system('clear')
   print "Opção inválida, selecione uma opção válida. \n"
   help()
   opcao = raw_input("Insira uma opção válida: ")
