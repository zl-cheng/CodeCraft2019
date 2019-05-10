package com.huawei;

import org.apache.log4j.Logger;

public class Main {
    private static final Logger logger = Logger.getLogger(Main.class);
    public static void main(String[] args) throws Exception
    {
        if (args.length != 5) {
            logger.error("please input args: inputFilePath, resultFilePath");
            return;
        }

        logger.info("Start...");

        String carPath = args[0];
        String roadPath = args[1];
        String crossPath = args[2];
        String presetAnswerPath = args[3];
        String answerPath = args[4];
        logger.info("carPath = " + carPath + " roadPath = " + roadPath + " crossPath = " + crossPath + " presetAnswerPath = " + presetAnswerPath + " and answerPath = " + answerPath);

        // TODO:read input files
        logger.info("start read input files");
        PleaseGetAnswer.getSolution(carPath,
                roadPath,
                crossPath,
                presetAnswerPath,
                answerPath);
        // TODO: calc

        // TODO: write answer.txt
        logger.info("Start write output file");

        logger.info("End...");
    }
}