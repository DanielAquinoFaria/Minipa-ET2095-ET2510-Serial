import serial
from bitstring import BitArray

ser = serial.Serial(port="COM1", baudrate=19200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE,
                    parity=serial.PARITY_NONE)


def to_binary(out):
    return BitArray(bytes(out)).bin


def data(num=11):

    seq_hex = []
    seq_bin = []
    display = []
    out = ser.read()
    if out.hex() == "8a":
        seq_bin.append(to_binary(out))
        seq_hex.append(out.hex())
        while len(seq_hex) < num:
            out = ser.read()
            seq_bin.append(to_binary(out))
            seq_hex.append(out.hex())

        virgula_posicao_temp = seq_hex[1]
        virgula = int(virgula_posicao_temp[1])

        # função de coleta dos algarismos da medida
        for i in range(2, 6):  # coleta os 4 caracteres dos display
            displayTemp = seq_hex[i]
            display.append(displayTemp[1])  # adiciona a lista o segundo termo do ‘item’ i de seq_hex

        # função para coleta da unidade e grandeza
        index_unidades = 0
        if seq_hex[6] == '3b': index_unidades = 0  # tensão
        if seq_hex[6] == 'b3': index_unidades = 1  # resistencia
        if seq_hex[6] == '31': index_unidades = 2  # diodo
        if seq_hex[6] == '3d': index_unidades = 3  # uA
        if seq_hex[6] == 'b6': index_unidades = 4  # capacitancia
        if seq_hex[6] == '32': index_unidades = 5  # frequencia
        if seq_hex[6] == 'b0': index_unidades = 6  # corrente

        table = [[[0.001, 'V'], [0.01, 'V'], [0.1, 'V'], [1, 'V'], [0.1, 'mV']],
                 [[0.1, 'Ohm'], [0.001, 'kOhm'], [0.01, 'kOhm'], [0.1, 'kOhm'], [0.001, 'MOhm'], [0.01, 'MOhm']],
                 [[0.001, 'V']],
                 [[0.1, 'uA'], [1, 'uA']],
                 [[0.001, 'nF'], [0.01, 'nF'], [0.1, 'nF'], [0.001, 'uF'], [0.01, 'uF'], [0.1, 'uF'], [0.001, 'mF']],
                 [[1, 'Hz'], [0.01, 'kHz'], [0.1, 'kHz'], [0.001, 'MHz'], [0.01, 'MHz']],
                 [[0.001, 'A'], [0.01, 'A']]]

        multiplo = table[index_unidades][virgula][0]
        unidade = table[index_unidades][virgula][1]
        display_info = (int(display[0]) * 1000 + int(display[1]) * 100 + int(display[2]) * 10 + int(display[3]))

        if display_info == 6000:   # cheack para overload
            medida = 'OL'
        else:
            medida = str(display_info * multiplo)[0:5]

        # bloco leitura polaridade
        if seq_hex[7] == '3e':
            polaridade = '-'
        else:
            polaridade = ' '

        # bloco de leitura do sinal alternado ou continuo
        if seq_hex[9] == 'ba':
            signal = 'DC'
        elif seq_hex[9] == 'b6':
            signal = 'AC'
        else:
            signal = ' '

        # função de info teporária
        # -------------'11111111111' apenas para ter o vusal do tamanho do array info_enabler
        info_enabler = '11111111111'
        output_temp_bin = []
        output_temp_hex = []
        for i in range(11):

            if info_enabler[i] == '1':
                output_temp_bin = output_temp_bin + seq_bin[i:i + 1]
                output_temp_hex = output_temp_hex + seq_hex[i:i + 1]
        # return "   " + "    |    ".join(output_temp_hex) + "\n" + " | ".join(output_temp_bin) + "\n"
        data_out = [polaridade, medida, unidade, signal]

        return data_out


if __name__ == '__main__':
    dados = [0]*4
    while True:
        dados = data()
        if str(type(dados)) == "<class 'list'>": # uma espera para o início dos dados
            print('medida: ', dados[0], dados[1], dados[2], dados[3])
