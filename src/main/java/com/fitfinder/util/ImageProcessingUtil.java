package com.fitfinder.util;

import lombok.extern.slf4j.Slf4j;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;

/**
 * Image Processing Utility - Handles image manipulation for virtual try-on
 * Uses Java AWT/ImageIO for image operations
 */
@Slf4j
public class ImageProcessingUtil {
    
    /**
     * Create a single garment virtual try-on image
     * Overlays cloth image on human image
     */
    public static void createSingleTryOnImage(String humanPath, String clothPath, String outputPath) throws IOException {
        try {
            // Read images
            BufferedImage human = ImageIO.read(new File(humanPath));
            BufferedImage cloth = ImageIO.read(new File(clothPath));
            
            if (human == null || cloth == null) {
                throw new IOException("Unable to read image files");
            }
            
            // Resize cloth to fit on human
            int clothWidth = (int) (human.getWidth() * 0.6);
            int clothHeight = (int) (human.getHeight() * 0.6);
            BufferedImage resizedCloth = resizeImage(cloth, clothWidth, clothHeight);
            
            // Create output image
            BufferedImage output = new BufferedImage(human.getWidth(), human.getHeight(), BufferedImage.TYPE_INT_RGB);
            Graphics2D g2d = output.createGraphics();
            
            // Draw human image
            g2d.drawImage(human, 0, 0, null);
            
            // Calculate position for cloth (center horizontally, quarter-way down vertically)
            int x = (human.getWidth() - resizedCloth.getWidth()) / 2;
            int y = (int) (human.getHeight() * 0.25);
            
            // Draw cloth image
            g2d.drawImage(resizedCloth, x, y, null);
            g2d.dispose();
            
            // Save output
            File outputFile = new File(outputPath);
            outputFile.getParentFile().mkdirs();
            ImageIO.write(output, "PNG", outputFile);
            
            log.info("Single try-on image created: {}", outputPath);
        } catch (IOException e) {
            log.error("Error creating try-on image", e);
            throw e;
        }
    }
    
    /**
     * Create a combo garment virtual try-on image (top + bottom)
     * Overlays top and bottom cloth images on human image
     */
    public static void createComboTryOnImage(String humanPath, String topPath, String bottomPath, String outputPath) throws IOException {
        try {
            // Read images
            BufferedImage human = ImageIO.read(new File(humanPath));
            BufferedImage top = ImageIO.read(new File(topPath));
            BufferedImage bottom = ImageIO.read(new File(bottomPath));
            
            if (human == null || top == null || bottom == null) {
                throw new IOException("Unable to read image files");
            }
            
            // Resize clothes
            int clothWidth = (int) (human.getWidth() * 0.6);
            int topHeight = (int) (human.getHeight() * 0.35);
            int bottomHeight = (int) (human.getHeight() * 0.35);
            
            BufferedImage resizedTop = resizeImage(top, clothWidth, topHeight);
            BufferedImage resizedBottom = resizeImage(bottom, clothWidth, bottomHeight);
            
            // Create output image
            BufferedImage output = new BufferedImage(human.getWidth(), human.getHeight(), BufferedImage.TYPE_INT_RGB);
            Graphics2D g2d = output.createGraphics();
            
            // Draw human image
            g2d.drawImage(human, 0, 0, null);
            
            // Calculate positions
            int x = (human.getWidth() - clothWidth) / 2;
            int yTop = (int) (human.getHeight() * 0.2);
            int yBottom = (int) (human.getHeight() * 0.55);
            
            // Draw top and bottom
            g2d.drawImage(resizedTop, x, yTop, null);
            g2d.drawImage(resizedBottom, x, yBottom, null);
            g2d.dispose();
            
            // Save output
            File outputFile = new File(outputPath);
            outputFile.getParentFile().mkdirs();
            ImageIO.write(output, "PNG", outputFile);
            
            log.info("Combo try-on image created: {}", outputPath);
        } catch (IOException e) {
            log.error("Error creating combo try-on image", e);
            throw e;
        }
    }
    
    /**
     * Resize image to specified dimensions
     */
    private static BufferedImage resizeImage(BufferedImage original, int width, int height) {
        BufferedImage resized = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        Graphics2D g2d = resized.createGraphics();
        g2d.drawImage(original, 0, 0, width, height, null);
        g2d.dispose();
        return resized;
    }
}
