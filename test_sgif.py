import sys
import os

# Add current directory to path so we can import gif_generator
sys.path.append(os.getcwd())

try:
    from gif_generator import generate_gif_bytes
    print("Import successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_generation():
    print("Testing GIF generation...")
    try:
        gif_bytes = generate_gif_bytes(
            text="Test GIF",
            frame_count=10,
            delay=100,
            font_path=None,
            text_color_param="red",
            width_pixels=300,
            theme="light",
            auto_wrap=False
        )
        
        if gif_bytes:
            with open("test_output.gif", "wb") as f:
                f.write(gif_bytes.getvalue())
            print("Success: GIF generated and saved to test_output.gif")
        else:
            print("Failure: No bytes returned.")
            
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
