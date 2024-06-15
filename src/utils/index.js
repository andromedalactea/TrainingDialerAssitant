import { useState, useEffect } from "react";

// Verifica si el error está relacionado con la clave pública faltante
export const isPublicKeyMissingError = ({ vapiError }) => {
  return vapiError?.message?.includes("missing public key");
};

// Simula la lectura de resultados de llamada desde un archivo
export const readCallResults = async (callId) => {
  // Aquí iría la lógica para leer un archivo de resultados de llamada
  // Para este ejemplo, simulamos una demora y devolvemos un resultado
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        callId,
        calification: JSON.stringify({
          "Order Accuracy": 9,
          "Customer Service": 10,
          "Speed": 8,
          "Notes": "Great job!",
        }),
      });
    }, 5000); // Simula una espera de 5 segundos
  });
};

