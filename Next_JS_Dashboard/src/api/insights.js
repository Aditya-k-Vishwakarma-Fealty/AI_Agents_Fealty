import client from "./client"

export const getRecruiterInsights = async () => {
  const response = await client.get("/insights")
  return response.data
}
