import serial


class ET2510:
    def __init__(self, com):
        self.ser = serial.Serial(port=com, baudrate=19200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE,
                                 parity=serial.PARITY_NONE)
        seq_hex = []
        while len(seq_hex) < 11:
            out = self.ser.read()
            seq_hex.append(out.hex())
        seq_hex.insert(0, seq_hex.pop(
            len(seq_hex) - 1))  # reorganiza a lista movendo todos os itens uma posição para direita

        self.seq_hex = seq_hex
        self.ser.close()
        self.table = [[[0.001, 'V', 0.5, 2, 0.9, 5], [0.01, 'V', 0.5, 2, 0.9, 5], [0.1, 'V', 0.5, 2, 0.9, 5],
                       [1, 'V', 0.5, 2, 0.9, 5], [0.1, 'mV', 0.5, 2, 0.9, 5]],
                      [[0.1, 'Ohm', 0.7, 2], [0.001, 'kOhm', 0.7, 2], [0.01, 'kOhm', 0.7, 2], [0.1, 'kOhm', 0.7, 2],
                       [0.001, 'MOhm', 1, 2], [0.01, 'MOhm', 1, 2]],
                      [[0.001, 'V', 1.5, 5]],
                      [[0.1, 'uA', 1, 2], [1, 'uA', 1, 2]],
                      [[0.001, 'nF', 1.9, 8], [0.01, 'nF', 1.9, 8], [0.1, 'nF', 1.9, 8], [0.001, 'uF', 1.9, 8],
                       [0.01, 'uF', 1.9, 8], [0.1, 'uF', 1.9, 8], [0.001, 'mF', 1.9, 8]],
                      [[1, 'Hz', 0.01, 1], [0.01, 'kHz', 0.01, 1], [0.1, 'kHz', 0.01, 1], [0.001, 'MHz', 0.01, 1],
                       [0.01, 'MHz', 0.01, 1]],
                      [[0.001, 'A', 1, 2, 1.5, 5], [0.01, 'A', 1, 2, 1.5, 5]]]
        self.unidades = {"3b": 0, "b3": 1, "31": 2, "3d": 3, "b6": 4, "32": 5, "b0": 6}
        self.tablei = None

    def chama_tabela(self, a):
        self.tablei = a
        valor = self.table[self.unidades.get(self.seq_hex[6])][self.virgula()][a]
        return valor

    def erro(self):
        """
        :return:
        .erro[0]: erro total
        .erro[1]: erro percentual
        .erro[2]: erro digital
        """
        # if self.seq_hex[6] == '31':
        err = self.chama_tabela(2)
        if self.display() == 'OL':
            erroPer = ''
            erroDig = ''
            erroTotal = ''
        else:
            if self.seq_hex[6] == '31':
                erroPer = str(round((float(self.display()) * err / 100), len(str(self.chama_tabela(0)))-3))
                digi = self.chama_tabela(3)
                erroDig = digi * self.chama_tabela(0)*10
            else:
                erroPer = str(round((float(self.display()) * err / 100), len(str(self.chama_tabela(0)))-2))
                digi = self.chama_tabela(3)
                erroDig = digi * self.chama_tabela(0)
            erroTotal = str(float(erroPer) + float(erroDig))[0:len(str(self.chama_tabela(0)))]

        return erroTotal, erroPer, erroDig

    def virgula(self):  # utilizado para referenciar unidade e grandeza na 'table'
        virgula = int(self.seq_hex[1][1])
        return virgula

    def display(self):
        display = []
        # função de coleta dos algarismos da medida
        for i in range(2, 6):  # coleta os 4 caracteres dos display
            displayTemp = self.seq_hex[i]
            display.append(displayTemp[1])  # adiciona a lista o segundo termo do ‘item’ i de seq_hex

        # função para coleta da unidade e grandeza
        multiplo = self.chama_tabela(0)
        display_info = (int(display[0]) * 1000 + int(display[1]) * 100 + int(display[2]) * 10 + int(display[3]))

        if display_info == 6000:  # check para overload
            medida = 'OL'
        elif self.seq_hex[6] == '31':
            if display_info >= 2758:
                medida = 'OL'
            else:
                medida = str(display_info * multiplo)[0:len(str(self.chama_tabela(0)))-1]
        else:
            medida = str(display_info * multiplo)[0:len(str(self.chama_tabela(0)))+2]
        return medida

    def unidade(self):  # unidade de medida
        unidade = self.chama_tabela(1)

        return unidade

    def polaridade(self):
        polaridade = []
        # bloco leitura polaridade
        if self.seq_hex[7] == '38':
            polaridade = '+'
        if self.seq_hex[7] == 'bc':
            polaridade = '-'
        if self.seq_hex[7] == 'b9':
            polaridade = ''
        return polaridade

    def acdc(self):  # ac dc
        if self.seq_hex[9] == 'ba' or '38':
            signal = 'DC'
        elif self.seq_hex[9] == 'b6' or '34':
            signal = 'AC'
        else:
            signal = ' '
        return signal


if __name__ == '__main__':
    while True:
        med = ET2510('COM1')
        print(med.polaridade(), med.display(), " ", med.unidade(), " ", med.acdc(), " ", med.erro()[0], " ",
              med.erro()[1], ' ', med.erro()[2])
