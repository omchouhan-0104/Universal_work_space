import api from "../api/axios";

export const processFile = async (
  fileId,
  operation,
  options = {}
) => {
  const response = await api.post(
    `/process/${fileId}`,
    {
      operation,
      options,
    }
  );

  return response.data;
};

