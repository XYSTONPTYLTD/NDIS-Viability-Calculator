import { GoogleGenAI } from "@google/genai";
import { ClientData, AnalysisResult } from "../types";

export const getGeminiAnalysis = async (data: ClientData, results: AnalysisResult): Promise<string> => {
  const apiKey = import.meta.env.VITE_GEMINI_API_KEY || process.env.GEMINI_API_KEY;
  
  if (!apiKey) {
    return "<p class='text-red-400'>API Key missing. Check .env.local</p>";
  }

  const ai = new GoogleGenAI({ apiKey });
  
  const prompt = `
    Act as a Senior NDIS Support Coordinator.
    Write a brief viability report (HTML format, using Tailwind classes for styling).
    
    Data:
    - Status: ${results.status}
    - Balance: $${data.currentBalance}
    - Weekly Cost: $${results.weeklyCost}
    - Plan Ends: ${results.planEndDateFormatted}
    - Surplus/Shortfall: $${results.surplusShortfall}
    
    Provide 3 strategic bullet points for the coordinator.
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash',
      contents: prompt,
    });
    return response.text() || "<p>No analysis generated.</p>";
  } catch (error) {
    return "<p>Error connecting to AI service.</p>";
  }
};
