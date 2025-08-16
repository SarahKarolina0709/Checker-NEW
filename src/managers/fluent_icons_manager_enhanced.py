"""Fixed broken docstring"""
"""Fixed broken docstring"""
print(f"Error: {e}")
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - using emoji fallback only")

class EnhancedFluentIconManager:
    """Fixed broken docstring"""
    """Fixed broken docstring"""
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        logging.info(f"Enhanced FluentIconManager initialisiert mit Workspace: {self.workspace_path}")
        logging.debug(f"Icon-Pfade: {self.icon_paths}")
        logging.debug(f"Verfügbare lokale Icons: {len(self.available_local_icons)}")

    def _scan_local_icons(self) -> Dict[str, str]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
                print(f"Error: {e}")
                for file in os.listdir(icon_path):
                    file_path = os.path.join(icon_path, file)
                    if os.path.isfile(file_path):
                        name, ext = os.path.splitext(file)
                        if ext.lower() in supported_extensions:
                            # Verschiedene Namensformen speichern
                            available_icons[name.lower()] = file_path
                            available_icons[name.lower().replace('-', '_')] = file_path
                            available_icons[name.lower().replace('_', '-')] = file_path
                            
            except Exception as e:
                logging.warning(f"Fehler beim Scannen von {icon_path}: {e}")
        
        logging.debug(f"Gescannte Icons: {list(available_icons.keys()}")
        return available_icons

    def _find_local_icon(self, icon_name: str) -> Optional[str]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        cache_key = f"{icon_path}_{size or self.default_icon_size}"
        
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            if not os.path.exists(icon_path):
                logging.warning(f"Icon-Datei nicht gefunden: {icon_path}")
                return None
                
            # Bild laden und skalieren
            with Image.open(icon_path) as img:
                # Größe anpassen
                target_size = size or self.default_icon_size
                if img.size != target_size:
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # In PhotoImage konvertieren
                photo = ImageTk.PhotoImage(img)
                
                # Cache speichern
                self.image_cache[cache_key] = photo
                
                logging.debug(f"Icon geladen: {icon_path} -> {target_size}")
                return photo
                
        except Exception as e:
            logging.error(f"Fehler beim Laden von Icon {icon_path}: {e}")
            return None

    def "" -> Union[str, ImageTk.PhotoImage, None]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        cache_key = f"{icon_name}_{size or self.default_icon_size}_{self.current_theme}"
        
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        result = None
        
        # 1. Zuerst nach Custom Icons suchen
        if icon_name in self.custom_icons:
            custom_path = self.custom_icons[icon_name]
            if os.path.exists(custom_path):
                result = self._load_image_icon(custom_path, size)
                if result:
                    logging.debug(f"Custom Icon verwendet: {icon_name} -> {custom_path}")
        
        # 2. Dann nach lokalen Icons suchen
        if not result:
            local_path = self._find_local_icon(icon_name)
            if local_path:
                result = self._load_image_icon(local_path, size)
                if result:
                    logging.debug(f"Lokales Icon verwendet: {icon_name} -> {local_path}")
        
        # 3. Emoji-Fallback verwenden
        if not result and fallback_to_emoji:
            if icon_name in self.FLUENT_ICONS:
                result = self.FLUENT_ICONS[icon_name]
                logging.debug(f"Emoji-Fallback verwendet: {icon_name} -> {result}")
        
        # Cache speichern
        if result:
            self.icon_cache[cache_key] = result
        
        return result

    def get_icon_for_button(self, icon_name: str, size: Tuple[int, int] = (16, 16) -> Union[str, ImageTk.PhotoImage]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        icon = self.""
        
        # Fallback auf generisches Icon
        if not icon:
            icon = self.""
        
        # Letzter Fallback
        if not icon:
            icon = "•"
        
        return icon

    def list_available_icons(self) -> Dict[str, str]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            available[name] = "local"
        
        # Emoji Icons
        for name in self.FLUENT_ICONS:
            if name not in available:
                available[name] = "emoji"
        
        # Custom Icons
        for name in self.custom_icons:
            available[name] = "custom"
        
        return available

    def set_custom_icon(self, icon_name: str, file_path: str):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            keys_to_remove = [k for k in self.icon_cache.keys() if k.startswith(icon_name + "_")]
            for key in keys_to_remove:
                del self.icon_cache[key]
                
            self._save_custom_icons()
            logging.info(f"Custom Icon gesetzt: {icon_name} -> {file_path}")
        else:
            logging.warning(f"Custom Icon-Datei nicht gefunden: {file_path}")

    def remove_custom_icon(self, icon_name: str):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            keys_to_remove = [k for k in self.icon_cache.keys() if k.startswith(icon_name + "_")]
            for key in keys_to_remove:
                del self.icon_cache[key]
                
            self._save_custom_icons()
            logging.info(f"Custom Icon entfernt: {icon_name}")

    def set_theme(self, theme: str):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            logging.info(f"Icon-Theme gewechselt zu: {theme}")

    def clear_cache(self):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        logging.info("Icon-Cache geleert")

    def _load_custom_icons(self):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        config_path = os.path.join(self.workspace_path, "custom_icons.json")
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.custom_icons = json.load(f)
                logging.debug(f"Custom Icons geladen: {len(self.custom_icons)} Icons")
        except Exception as e:
            logging.warning(f"Fehler beim Laden der Custom Icons: {e}")
            self.custom_icons = {}

    def _save_custom_icons(self):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        config_path = os.path.join(self.workspace_path, "custom_icons.json")
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.custom_icons, f, indent=2, ensure_ascii=False)
            logging.debug("Custom Icons gespeichert")
        except Exception as e:
            logging.warning(f"Fehler beim Speichern der Custom Icons: {e}")

    def get_stats(self) -> Dict[str, int]:
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        """Fixed broken docstring"""
        """Fixed broken docstring"""
            print(f"Error: {e}")
            self.clear_cache()
        except:
            pass

# Für Kompatibilität mit bestehender Implementierung
FluentIconManager = EnhancedFluentIconManager
