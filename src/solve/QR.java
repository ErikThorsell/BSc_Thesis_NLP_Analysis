package nlptest1;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.Scanner;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

public class QR {

    public static void main(String[] args) throws Exception {

    int antalRatt = 0;
    int antalFel = 0;

    File folder = new File("PATH/TO/FOLDER/WITH/CALLS");
    File[] listOfFiles = folder.listFiles();

    Scanner facit = new Scanner(new File("PATH/TO/SOLUTIONS/MANUAL"));
    PrintWriter utfil = new PrintWriter(new BufferedWriter(new FileWriter("PATH/TO/PRINT/RESULTS")));
    ArrayList<String[]> afacit = new ArrayList<String[]>();

    while (facit.hasNextLine()) {
        String[] rad = facit.nextLine().split(",");
        if (rad.length < 17) {
        continue;
        }
        rad[0] = rad[0].split("-")[1] + ".txt.out";
        afacit.add(rad);
    }
    facit.close();

    int antalSamtal = 0;

    for (int i = 0; i < listOfFiles.length; i++) {
        if (!listOfFiles[i].isFile()) {
        System.out.println("Inte fil");
        continue;
        }
        Scanner sjukdomar = new Scanner(new File("sjukdomar.txt"));
        LinkedHashMap<String, Boolean> hSjukdomar = new LinkedHashMap<String, Boolean>();

        while (sjukdomar.hasNextLine()) {
        hSjukdomar.put(sjukdomar.nextLine().toLowerCase(), false);
        }
        sjukdomar.close();

        File inputFile = listOfFiles[i];
        try {
        DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
        DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();

        Document doc = dBuilder.parse(inputFile);
        doc.getDocumentElement().normalize();

        Element eRoot = doc.getDocumentElement();

        NodeList nDocuments = eRoot.getElementsByTagName("document");
        NodeList nSentences = ((Element) nDocuments.item(0)).getElementsByTagName("sentences");
        NodeList nSentence = ((Element) nSentences.item(0)).getElementsByTagName("sentence");

        for (int temp = 0; temp < nSentence.getLength(); temp++) {
            NodeList nTokens = eSentence.getElementsByTagName("tokens");
            NodeList nDependencies = eSentence.getElementsByTagName("dependencies");
            NodeList nToken = ((Element) nTokens.item(0)).getElementsByTagName("token");

            NodeList firstnWord = ((Element) nToken.item(0)).getElementsByTagName("word");
            String firstWord = firstnWord.item(0).getTextContent();

            NodeList lastnToken = ((Element) nTokens.item(0)).getElementsByTagName("token");
            NodeList lastnWord = ((Element) lastnToken.item(lastnToken.getLength() - 1)).getElementsByTagName("word");
            String lastWord = lastnWord.item(0).getTextContent();

            if (firstWord.equals("D") || firstWord.equals("N")|| firstWord.equals("S") || lastWord.equals("?")) {
            continue;
            }

            boolean inteAktuellt = false;
            for (int a = 0; a < nToken.getLength(); a++) {
            NodeList inteWords = ((Element) nToken.item(a)).getElementsByTagName("word");
            String inteWord = inteWords.item(0).getTextContent().toLowerCase();

            if (inteWord.equals("misstänkt") || inteWord.equals("utesluta") || inteWord.equals("aldrig ")) {
                inteAktuellt = true;
            }
            if (inteWord.equals("aldrig")) {
                for (int b = a; b < nToken.getLength(); b++) {
                NodeList aktuellWords = ((Element) nToken.item(b)).getElementsByTagName("word");
                String aktuellWord = aktuellWords.item(0).getTextContent().toLowerCase();
                if (aktuellWord.equals("har")) {
                    inteAktuellt = true;

                }
                }
                inteAktuellt = true;
            }
            if( inteWord.equals("har") || inteWord.equals("i")){
                for (int b = a; b < nToken.getLength(); b++) {
                    NodeList aktuellWords = ((Element) nToken.item(b)).getElementsByTagName("word");
                    String aktuellWord = aktuellWords.item(0).getTextContent().toLowerCase();

                    if (aktuellWord.equals("haft")|| inteWord.equals("somras") || inteWord.equals("vintras")|| inteWord.equals("höstas") || inteWord.equals("botten")){

                        for (int j = 0; j < nDependencies.getLength(); j++) {
                            NodeList nDep = ((Element) nDependencies.item(j)).getElementsByTagName("dep");
                            for (int k = 0; k < nDep.getLength(); k++) {
                                if (((Element) nDep.item(k)).getAttribute("type").equals("nmod:i")) {
                                    Element eGovernor = (Element) ((Element) nDep.item(k)).getElementsByTagName("governor").item(0);
                                    Element eDependent = (Element) ((Element) nDep.item(k)).getElementsByTagName("dependent").item(0);

                                    if (eGovernor.getTextContent().toLowerCase().equals("ont")) {
                                        if (!hSjukdomar.containsKey("ont i " + eDependent.getTextContent())
                                                || !hSjukdomar.containsKey("ont i " + eDependent.getTextContent())) {
                                            hSjukdomar.put("ont i " + eDependent.getTextContent(), Boolean.TRUE);
                                        }
                                    }
                                }
                            }

                        }

            for (int j = 0; j < nToken.getLength(); j++) {

            NodeList nWords = ((Element) nToken.item(j)).getElementsByTagName("word");
            String ontWord = nWords.item(0).getTextContent().toLowerCase();

            if (ontWord.equals("ont")) {
                NodeList niWords = ((Element) nToken.item(j + 1)).getElementsByTagName("word");
                String ontiWord = niWords.item(0).getTextContent().toLowerCase();
                if (ontiWord.equals("i")) {
                NodeList iWord = ((Element) nToken.item(j + 1 + 1)).getElementsByTagName("word");
                String onti = iWord.item(0).getTextContent().toLowerCase();
                if (!(hSjukdomar.containsKey(onti) || hSjukdomar.containsKey("ont i " + onti)) && !(onti.equals("") || onti.equals("-"))) {
                    System.out.println("Lägger till ont i " + onti);
                    hSjukdomar.put("ont i " + onti, Boolean.TRUE);
                }
                }
            }

            NodeList nWord = ((Element) nToken.item(j)).getElementsByTagName("word");
            String sWord = nWord.item(0).getTextContent();

            String[] asjukdomar = (String[]) hSjukdomar.keySet().toArray(new String[0]);

            for (int m = 0; m < asjukdomar.length; m++) {
                String s = asjukdomar[m];
                if (s.toLowerCase().compareTo(sWord.toLowerCase()) == 0) {

                boolean sjuk = true;
                for (int l = 0; l < nDependencies.getLength(); l++) {
                    NodeList nDep = ((Element) nDependencies.item(l)).getElementsByTagName("dep");
                    for (int k = 0; k < nDep.getLength(); k++) {
                    if (((Element) nDep.item(k)).getAttribute("type").startsWith("det")) {
                        Element eGovernor = (Element) ((Element) nDep.item(k)).getElementsByTagName("governor").item(0);
                        Element eDependent = (Element) ((Element) nDep.item(k)).getElementsByTagName("dependent").item(0);

                        if (eGovernor.getTextContent().toLowerCase().equals(s)
                            && eDependent.getTextContent().toLowerCase().equals("ingen")) {
                            sjuk = false;
                        }
                        if (eGovernor.getTextContent().toLowerCase().equals(s)
                            && eDependent.getTextContent().toLowerCase().equals("inte")) {
                            sjuk = false;
                        }
                    }
                    }
                }

                if (!sjuk) {
                    hSjukdomar.remove(s);
                    continue;
                }

                if (!hSjukdomar.get(s)) {
                    hSjukdomar.put(s, Boolean.TRUE);
                }

                }
            }
            }

                    }
                }
            }
            }
            if (inteAktuellt == true) {
            continue;
            }
        }

        int count = 0;
        for (boolean b : hSjukdomar.values()) {
            if (b == true) {
            count = count + 1;
            }
        }

        boolean hittaFil = false;

        for (int nFil = 0; nFil < afacit.size(); nFil++) {
            String[] rad = afacit.get(nFil);

            if (rad[0].equals(inputFile.getName())) {
            hittaFil = true;
            int svar = 0;
            if (count > 3) {
                svar = 1;
                utfil.println(inputFile.getName() + " 1");
            } else {
                utfil.println(inputFile.getName() + " 0");
            }
            try {
                if (Integer.parseInt(rad[17]) != svar) {
                antalFel = antalFel + 1;

                } else {
                antalRatt = antalRatt + 1;
                }
            } catch (Exception e) {
            }

            }

        }

        if (hittaFil == false) {

        }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    utfil.close();

    }
}
