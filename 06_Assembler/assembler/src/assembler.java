import java.io.*;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.Scanner;

class assembler {
    public static void main(String[] args) throws IOException {
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

        int rom_address = 0;
        int next_variable_address = 16;
        ArrayList<String> instructions_only = new ArrayList<String>();
        ArrayList<String> output_lines = new ArrayList<String>();
        File file = new File(args[0]);
        File tempFile = new File("temp.asm");
        BufferedReader reader = new BufferedReader(new FileReader(file));
        BufferedReader writer = new BufferedReader(new FileWriter(tempFile));



    }
}