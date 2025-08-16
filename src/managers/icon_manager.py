"""Fixed broken docstring"""
"""Fixed broken docstring"""
"""Centralized icon management system"""Fixed broken docstring"""
        self.logger.info(f"Icon manager initialized with assets path: {self.assets_path}")
    
    def "", color=None):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        cache_key = f"{icon_name}_{size[0]}x{size[1]}_{color}"
        
        # Check cache first
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        # Try to load PNG icon
        png_path = self.assets_path / f"{icon_name}.png"
        if png_path.exists():
            try:
                pass
            except Exception as e:
                print(f"Error: {e}")
                image = Image.open(png_path)
                if color:
                    # Apply color if specified (simplified approach)
                    image = self._apply_color_to_image(image, color)
                
                ctk_image = ctk.CTkImage(light_image=image, size=size)
                self.icon_cache[cache_key] = ctk_image
                return ctk_image
                
            except Exception as e:
                self.logger.warning(f"Could not load PNG icon {icon_name}: {e}")
        
        # Fall back to text icon
        text_icon = self.text_icons.get(icon_name, fallback_text)
        self.icon_cache[cache_key] = text_icon
        return text_icon
    
    def get_text_icon(self, icon_name, fallback='?'):
        """Get text representation of an icon"""Fixed broken docstring"""
        """Preload icons into cache"""Fixed broken docstring"""
        self.logger.info(f"Preloading {len(icon_names)} icons")
        
        for icon_name in icon_names:
            self.""
        
        self.logger.info("Icon preloading complete")
    
    def _apply_color_to_image(self, image, color):
        """Apply color to an image (simplified implementation)"""Fixed broken docstring"""
            print(f"Error: {e}")
            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Simple color overlay (this is a basic implementation)
            # For more sophisticated coloring, you'd need more complex image processing
            return image
            
        except Exception as e:
            self.logger.warning(f"Could not apply color to image: {e}")
            return image
    
    def create_icon_button(self, parent, icon_name, text="", command=None, **kwargs):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        icon = self.""
        
        # Create button
        if isinstance(icon, str):
            # Text icon - prepend to text
            button_text = f"{icon} {text}".strip()
            button = ctk.CTkButton()
                parent
                text=button_text
                command=command
                **kwargs
            )
        else:
            # Image icon
            button = ctk.CTkButton()
                parent
                text=text
                image=icon
                command=command
                **kwargs
            )
        
        return button
    
    def clear_cache(self):
        """Clear the icon cache"""Fixed broken docstring"""
        self.logger.info("Icon cache cleared")
    
    def get_cache_info(self):
        """Get information about the icon cache"""Fixed broken docstring"""
    """Get the global icon manager instance"""Fixed broken docstring"""