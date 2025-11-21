
import { GoogleGenAI } from "@google/genai";
import { ClientData, AnalysisResult } from "../types";

export const getGeminiAnalysis = async (data: ClientData, results: AnalysisResult): Promise<string> => {
  if (!process.env.API_KEY) {
    return "<p class='text-red-400'>API Key not found. Unable to generate AI analysis.</p>";
  }

  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const todayStr = new Date().toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' });

  const prompt = `
    Act as a Senior Independent NDIS Support Coordinator (Fail-Safe Specialist) with 15 years of experience in the Australian disability sector.
    
    **Task:** Write a formal, holistic "Viability & Strategy Report" for a participant's file.
    
    **Strict Style & Formatting Guidelines:**
    1. **Format:** Return ONLY raw, valid HTML code. Do not use Markdown code blocks (like \`\`\`html).
    2. **Styling:** Use Tailwind CSS classes for layout. 
       - Use <table> with classes: "w-full border-collapse border border-slate-700 text-sm my-4".
       - Use <th> with classes: "border border-slate-700 bg-slate-800 p-2 text-left text-slate-200".
       - Use <td> with classes: "border border-slate-700 p-2 text-slate-300".
    3. **Language:** Strict Professional Australian English (e.g., 'utilised', 'maximise', 'program', 'modelled').
    4. **Tone:** Holistic, carefully worded, protective of the coordinator's liability, and strategically sharp. Avoid colloquialisms.

    **Report Structure:**
    
    <h3>1. Executive Summary</h3>
    <p>[Provide a holistic summary of the current position. Is the funding sustainable? What is the primary risk?]</p>

    <h3>2. Financial Trajectory Analysis</h3>
    [Insert an HTML Table comparing the 'Current Status' vs 'Required for Sustainability']
    - Columns: Metric, Current Value, Target/Safe Value, Variance.
    - Metrics to include: Weekly Burn Rate, Projected End Date, Surplus/Shortfall.

    <h3>3. Strategic Recommendations</h3>
    [Provide 3-4 bullet points using <ul> and <li> tags. Focus on capacity building, safeguarding, and evidence collection for the next review.]

    **Case Data:**
    - **Plan Context:** Plan ends on ${results.planEndDateFormatted} (${results.weeksRemaining.toFixed(1)} weeks remaining).
    - **Portal Truth:** Current Balance is $${data.currentBalance.toLocaleString()}.
    - **Billing Model:** Currently billing ${data.hoursPerWeek} hours/week ($${results.weeklyCost.toFixed(2)}/week).
    - **Projected Outcome:** ${results.runwayWeeks.toFixed(1)} weeks runway. 
    - **Gap Analysis:** The participant has a buffer of ${results.bufferWeeks.toFixed(1)} weeks relative to the plan end date.
    - **Financial Outcome:** Projected ${results.surplusShortfall >= 0 ? 'Surplus' : 'Shortfall'} of $${Math.abs(results.surplusShortfall).toLocaleString()}.
    - **System Verdict:** ${results.status}
    - **Immediate Advice:** ${results.instantAdvice.header}

    **Constraint:** Do not output any text outside the HTML tags. Start directly with the HTML content.
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
    });
    return response.text || "<p>No analysis generated.</p>";
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "<p>Error generating analysis.</p>";
  }
};
