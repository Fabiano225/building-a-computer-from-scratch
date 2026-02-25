import java.io.*;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;

class Assembler {
    public static void main(String[] args) {
        Map<String, String> destTable = Map.of(
                "null", "000", "M", "001", "D", "010", "MD", "011",
                "A", "100", "AM", "101", "AD", "110", "AMD", "111"
        );

        Map<String, String> jumpTable = Map.of(
                "null", "000", "JGT", "001", "JEQ", "010", "JGE", "011",
                "JLT", "100", "JNE", "101", "JLE", "110", "JMP", "111"
        );

        Map<String, String> compTable = new HashMap<>();
        Map<String, Integer> symbolTable = new HashMap<>();

        compTable.put("0",   "0101010"); compTable.put("1",   "0111111");
        compTable.put("-1",  "0111010"); compTable.put("D",   "0001100");
        compTable.put("A",   "0110000"); compTable.put("M",   "1110000");
        compTable.put("!D",  "0001101"); compTable.put("!A",  "0110001");
        compTable.put("!M",  "1110001"); compTable.put("-D",  "0001111");
        compTable.put("-A",  "0110011"); compTable.put("-M",  "1110011");
        compTable.put("D+1", "0011111"); compTable.put("A+1", "0110111");
        compTable.put("M+1", "1110111"); compTable.put("D-1", "0001110");
        compTable.put("A-1", "0110010"); compTable.put("M-1", "1110010");
        compTable.put("D+A", "0000010"); compTable.put("D+M", "1000010");
        compTable.put("D-A", "0010011"); compTable.put("D-M", "1010011");
        compTable.put("A-D", "0000111"); compTable.put("M-D", "1000111");
        compTable.put("D&A", "0000000"); compTable.put("D&M", "1000000");
        compTable.put("D|A", "0010101"); compTable.put("D|M", "1010101");

        symbolTable.put("SP", 0); symbolTable.put("LCL", 1);
        symbolTable.put("ARG", 2); symbolTable.put("THIS", 3);
        symbolTable.put("THAT", 4); symbolTable.put("SCREEN", 16384);
        symbolTable.put("KBD", 24576);
        for (int i = 0; i <= 15; i++) {
            symbolTable.put("R" + i, i);
        }

        int romAddress = 0;
        int nextVariableAddress = 16;
        ArrayList<String> instructionsOnly = new ArrayList<>();
        ArrayList<String> outputLines = new ArrayList<>();
        String inputFileName = args[0];

        try (BufferedReader reader = new BufferedReader(new FileReader(inputFileName))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String cleanLine = line.split("//")[0].trim();
                if (cleanLine.isEmpty()) {
                    continue;
                }

                if (cleanLine.startsWith("(") && cleanLine.endsWith(")")) {
                    String label = cleanLine.substring(1, cleanLine.length() - 1).trim();
                    symbolTable.put(label, romAddress);
                } else {
                    instructionsOnly.add(cleanLine);
                    romAddress++;
                }
            }
        } catch (IOException e) {
            System.err.println("Fehler beim Lesen der Datei: " + e.getMessage());
            return;
        }

        for (String line : instructionsOnly) {
            if (line.startsWith("@")) {
                String symbol = line.substring(1).trim();
                int value;

                if (symbol.matches("\\d+")) {
                    value = Integer.parseInt(symbol);
                } else if (symbolTable.containsKey(symbol)) {
                    value = symbolTable.get(symbol);
                } else {
                    symbolTable.put(symbol, nextVariableAddress);
                    value = nextVariableAddress;
                    nextVariableAddress++;
                }

                String binaryA = String.format("%16s", Integer.toBinaryString(value)).replace(' ', '0');
                outputLines.add(binaryA);

            } else {
                String destPart = "null";
                String jumpPart = "null";
                String compPart;
                String rest = line;

                if (rest.contains("=")) {
                    String[] parts = rest.split("=", 2);
                    destPart = parts[0];
                    rest = parts[1];
                }

                if (rest.contains(";")) {
                    String[] parts = rest.split(";", 2);
                    compPart = parts[0];
                    jumpPart = parts[1];
                } else {
                    compPart = rest;
                }

                String cBits = compTable.get(compPart);
                String dBits = destTable.get(destPart);
                String jBits = jumpTable.get(jumpPart);

                String binaryC = "111" + cBits + dBits + jBits;
                outputLines.add(binaryC);
            }
        }

        String outputFilename;
        int dotIndex = inputFileName.lastIndexOf('.');
        if (dotIndex != -1) {
            outputFilename = inputFileName.substring(0, dotIndex) + ".hack";
        } else {
            outputFilename = inputFileName + ".hack";
        }

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputFilename))) {
            for (int i = 0; i < outputLines.size(); i++) {
                writer.write(outputLines.get(i));
                if (i < outputLines.size() - 1) {
                    writer.newLine();
                }
            }
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}