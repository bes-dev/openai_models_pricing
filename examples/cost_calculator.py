#!/usr/bin/env python3
"""
OpenAI Cost Calculator

This script demonstrates how to calculate costs for different OpenAI models
using the pricing data from the API.

Usage:
    python cost_calculator.py
"""

import requests
from typing import Dict, Any, Optional


class OpenAICostCalculator:
    """Calculate costs for OpenAI API usage based on current pricing."""

    def __init__(self, api_url: str = "https://bes-dev.github.io/openai_models_pricing/api.json"):
        """Initialize calculator with pricing data from API or local file."""
        self.pricing = self._load_pricing(api_url)

    def _load_pricing(self, url: str) -> Dict[str, Any]:
        """Load pricing data from API or local file."""
        import json
        import os

        # Try to load from local file first (for development/testing)
        local_path = "github_pages/api.json"
        if os.path.exists(local_path):
            print(f"Loading pricing from local file: {local_path}")
            with open(local_path, 'r') as f:
                data = json.load(f)
                return data['models']

        # Otherwise load from remote URL
        print(f"Loading pricing from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['models']

    def get_model_pricing(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get pricing data for a specific model."""
        # Try exact match first
        if model_name in self.pricing:
            return self.pricing[model_name]

        # Try case-insensitive partial match
        model_lower = model_name.lower()
        for key, value in self.pricing.items():
            if model_lower in key.lower():
                return value

        return None

    def calculate_language_model_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        cached_input_tokens: int = 0
    ) -> Dict[str, float]:
        """
        Calculate cost for language models (GPT-4, GPT-3.5, etc.).

        Args:
            model_name: Name of the model (e.g., "gpt-4o", "gpt-3.5-turbo")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cached_input_tokens: Number of cached input tokens (if supported)

        Returns:
            Dictionary with cost breakdown
        """
        model = self.get_model_pricing(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found in pricing data")

        if model['pricing_type'] != 'per_1m_tokens':
            raise ValueError(f"Model '{model_name}' is not a token-based language model")

        # Calculate costs (prices are per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * model.get('input', 0)
        output_cost = (output_tokens / 1_000_000) * model.get('output', 0)
        cached_cost = (cached_input_tokens / 1_000_000) * model.get('cached_input', 0)

        total_cost = input_cost + output_cost + cached_cost

        return {
            'model': model['model'],
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cached_input_tokens': cached_input_tokens,
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'cached_input_cost': round(cached_cost, 6),
            'total_cost': round(total_cost, 6),
        }

    def calculate_image_generation_cost(
        self,
        model_name: str,
        num_images: int = 1,
        resolution: str = "1024x1024",
        quality: str = "low",
        input_tokens: int = 0,
        output_tokens: int = 0
    ) -> Dict[str, float]:
        """
        Calculate cost for token-based image generation models (gpt-image-1).

        Args:
            model_name: Name of the model (e.g., "gpt-image-1")
            num_images: Number of images to generate
            resolution: Image resolution (e.g., "1024x1024", "1024x1536")
            quality: Image quality ("low", "standard", "high")
            input_tokens: Number of input tokens (for text prompt)
            output_tokens: Number of output tokens

        Returns:
            Dictionary with cost breakdown
        """
        model = self.get_model_pricing(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found in pricing data")

        # Calculate text token costs
        text_input_cost = (input_tokens / 1_000_000) * model.get('input', 0)
        text_output_cost = (output_tokens / 1_000_000) * model.get('output', 0)

        # Calculate image generation cost
        image_cost = 0
        if 'image_pricing' in model:
            if quality in model['image_pricing']:
                if resolution in model['image_pricing'][quality]:
                    price_per_image = model['image_pricing'][quality][resolution]
                    image_cost = num_images * price_per_image
                else:
                    available = list(model['image_pricing'][quality].keys())
                    raise ValueError(f"Resolution '{resolution}' not available. Available: {available}")
            else:
                available = list(model['image_pricing'].keys())
                raise ValueError(f"Quality '{quality}' not available. Available: {available}")

        total_cost = text_input_cost + text_output_cost + image_cost

        return {
            'model': model['model'],
            'num_images': num_images,
            'resolution': resolution,
            'quality': quality,
            'text_input_cost': round(text_input_cost, 6),
            'text_output_cost': round(text_output_cost, 6),
            'image_cost': round(image_cost, 6),
            'total_cost': round(total_cost, 6),
        }

    def calculate_dalle_cost(
        self,
        model_name: str,
        num_images: int = 1,
        resolution: str = "1024x1024",
        quality: str = "standard"
    ) -> Dict[str, float]:
        """
        Calculate cost for DALL-E models (fixed price per image).

        Args:
            model_name: Name of the model (e.g., "dall-e-3", "dall-e-2")
            num_images: Number of images to generate
            resolution: Image resolution
            quality: Image quality

        Returns:
            Dictionary with cost breakdown
        """
        model = self.get_model_pricing(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found in pricing data")

        # Get price from image_pricing
        if 'image_pricing' not in model:
            raise ValueError(f"Model '{model_name}' does not have image pricing data")

        if quality not in model['image_pricing']:
            available = list(model['image_pricing'].keys())
            raise ValueError(f"Quality '{quality}' not available. Available: {available}")

        if resolution not in model['image_pricing'][quality]:
            available = list(model['image_pricing'][quality].keys())
            raise ValueError(f"Resolution '{resolution}' not available. Available: {available}")

        price_per_image = model['image_pricing'][quality][resolution]
        total_cost = num_images * price_per_image

        return {
            'model': model['model'],
            'num_images': num_images,
            'resolution': resolution,
            'quality': quality,
            'price_per_image': round(price_per_image, 6),
            'total_cost': round(total_cost, 6),
        }

    def calculate_audio_cost(
        self,
        model_name: str,
        duration_minutes: float
    ) -> Dict[str, float]:
        """
        Calculate cost for audio transcription (Whisper).

        Args:
            model_name: Name of the model (e.g., "whisper")
            duration_minutes: Audio duration in minutes

        Returns:
            Dictionary with cost breakdown
        """
        model = self.get_model_pricing(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found in pricing data")

        if model['pricing_type'] != 'per_minute':
            raise ValueError(f"Model '{model_name}' is not priced per minute")

        price_per_minute = model.get('price', 0)
        total_cost = duration_minutes * price_per_minute

        return {
            'model': model['model'],
            'duration_minutes': duration_minutes,
            'price_per_minute': round(price_per_minute, 6),
            'total_cost': round(total_cost, 6),
        }


def main():
    """Demonstrate cost calculations for different models."""

    print("OpenAI Cost Calculator\n" + "=" * 50 + "\n")

    # Initialize calculator
    calculator = OpenAICostCalculator()

    # Example 1: GPT-4o language model
    print("Example 1: GPT-4o Language Model")
    print("-" * 50)
    result = calculator.calculate_language_model_cost(
        model_name="gpt-4o",
        input_tokens=500,
        output_tokens=1500
    )
    print(f"Model: {result['model']}")
    print(f"Input: {result['input_tokens']} tokens → ${result['input_cost']:.6f}")
    print(f"Output: {result['output_tokens']} tokens → ${result['output_cost']:.6f}")
    print(f"Total Cost: ${result['total_cost']:.6f}\n")

    # Example 2: GPT-4o with cached input
    print("Example 2: GPT-4o with Cached Input")
    print("-" * 50)
    result = calculator.calculate_language_model_cost(
        model_name="gpt-4o",
        input_tokens=100,
        output_tokens=500,
        cached_input_tokens=1000
    )
    print(f"Model: {result['model']}")
    print(f"New Input: {result['input_tokens']} tokens → ${result['input_cost']:.6f}")
    print(f"Cached Input: {result['cached_input_tokens']} tokens → ${result['cached_input_cost']:.6f}")
    print(f"Output: {result['output_tokens']} tokens → ${result['output_cost']:.6f}")
    print(f"Total Cost: ${result['total_cost']:.6f}\n")

    # Example 3: gpt-image-1 (token-based image generation)
    print("Example 3: gpt-image-1 Quality Comparison")
    print("-" * 50)

    for quality in ['low', 'medium', 'high']:
        try:
            result = calculator.calculate_image_generation_cost(
                model_name="gpt-image-1",
                num_images=1,
                resolution="1024x1024",
                quality=quality,
                input_tokens=50,
                output_tokens=200
            )
            print(f"{quality.capitalize():8} quality: Text ${result['text_input_cost'] + result['text_output_cost']:.4f} + Image ${result['image_cost']:.4f} = Total ${result['total_cost']:.4f}")
        except ValueError:
            pass
    print()

    # Example 4: DALL-E 3
    print("Example 4: DALL-E 3")
    print("-" * 50)
    result = calculator.calculate_dalle_cost(
        model_name="dall-e-3",
        num_images=5,
        resolution="1024x1024",
        quality="standard"
    )
    print(f"Model: {result['model']}")
    print(f"Images: {result['num_images']} × {result['resolution']} ({result['quality']})")
    print(f"Price per Image: ${result['price_per_image']:.6f}")
    print(f"Total Cost: ${result['total_cost']:.6f}\n")

    # Example 5: Whisper audio transcription (if available)
    print("Example 5: Whisper Audio Transcription")
    print("-" * 50)
    try:
        result = calculator.calculate_audio_cost(
            model_name="whisper",
            duration_minutes=15.5
        )
        print(f"Model: {result['model']}")
        print(f"Duration: {result['duration_minutes']} minutes")
        print(f"Price per Minute: ${result['price_per_minute']:.6f}")
        print(f"Total Cost: ${result['total_cost']:.6f}\n")
    except ValueError as e:
        print(f"Note: Whisper model not found in current pricing data.")
        print(f"      This may be added in future updates.\n")

    # Comparison: Generate 100 images with different models
    print("Comparison: Generate 100 images (1024x1024)")
    print("-" * 50)

    models_to_compare = [
        ("gpt-image-1-mini", "low"),
        ("gpt-image-1", "low"),
        ("gpt-image-1-mini", "medium"),
        ("dall-e-2", "standard"),
        ("gpt-image-1-mini", "high"),
        ("gpt-image-1", "medium"),
        ("dall-e-3", "standard"),
        ("gpt-image-1", "high"),
    ]

    for model_name, quality in models_to_compare:
        try:
            if "dall-e" in model_name:
                result = calculator.calculate_dalle_cost(
                    model_name=model_name,
                    num_images=100,
                    resolution="1024x1024",
                    quality=quality
                )
                total = result['total_cost']
            else:
                result = calculator.calculate_image_generation_cost(
                    model_name=model_name,
                    num_images=100,
                    resolution="1024x1024",
                    quality=quality,
                    input_tokens=1000,
                    output_tokens=5000
                )
                total = result['total_cost']

            print(f"{model_name:20} ({quality:8}): ${total:7.2f}")
        except Exception as e:
            print(f"{model_name:20} ({quality:8}): Error - {e}")


if __name__ == "__main__":
    main()
