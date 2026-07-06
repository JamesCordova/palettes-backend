-- ============================================
-- USERS
-- ============================================
CREATE TABLE users (
  id            SERIAL PRIMARY KEY,
  username      VARCHAR(50) UNIQUE NOT NULL,
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  avatar_url    VARCHAR(255),
  created_at    TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- PALETTES
-- ============================================
CREATE TABLE palettes (
  id            SERIAL PRIMARY KEY,
  user_id       INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name          VARCHAR(100) NOT NULL,
  description   TEXT,
  is_public     BOOLEAN DEFAULT true,
  forked_from   INT NULL REFERENCES palettes(id) ON DELETE SET NULL,
  created_at    TIMESTAMP DEFAULT NOW(),
  updated_at    TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- COLOR CATALOG (global, normalized, one row per unique hex)
-- Powers color trend analytics across the whole platform
-- ============================================
CREATE TABLE color_catalog (
  hex_code    VARCHAR(7) PRIMARY KEY,   -- e.g. #FF5733
  hue         SMALLINT NOT NULL,        -- 0-360°
  saturation  SMALLINT NOT NULL,        -- 0-100%
  lightness   SMALLINT NOT NULL,        -- 0-100%
  luminance   NUMERIC(5,2) NOT NULL,    -- perceived brightness, 0-255
  usage_count INT DEFAULT 0,            -- denormalized counter, updated via trigger/app logic
  created_at  TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- PALETTE_COLORS (join table: which colors belong to which palette, in what order)
-- ============================================
CREATE TABLE palette_colors (
  id          SERIAL PRIMARY KEY,
  palette_id  INT NOT NULL REFERENCES palettes(id) ON DELETE CASCADE,
  hex_code    VARCHAR(7) NOT NULL REFERENCES color_catalog(hex_code),
  name        VARCHAR(50),              -- local/custom name, can vary per palette
  position    SMALLINT NOT NULL,
  UNIQUE (palette_id, position)
);

-- ============================================
-- FAVORITES (many-to-many: users <-> palettes)
-- ============================================
CREATE TABLE favorites (
  user_id     INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  palette_id  INT NOT NULL REFERENCES palettes(id) ON DELETE CASCADE,
  created_at  TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (user_id, palette_id)
);

-- ============================================
-- TAGS (optional categorization)
-- ============================================
CREATE TABLE tags (
  id    SERIAL PRIMARY KEY,
  name  VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE palette_tags (
  palette_id  INT NOT NULL REFERENCES palettes(id) ON DELETE CASCADE,
  tag_id      INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (palette_id, tag_id)
);

-- ============================================
-- TRIGGER FUNCTIONS: keep usage_count in sync
-- ============================================

-- Increment on insert (color added to a palette)
CREATE OR REPLACE FUNCTION increment_color_usage() RETURNS TRIGGER AS $$
BEGIN
  UPDATE color_catalog 
  SET usage_count = usage_count + 1 
  WHERE hex_code = NEW.hex_code;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Decrement on delete (color removed from a palette)
CREATE OR REPLACE FUNCTION decrement_color_usage() RETURNS TRIGGER AS $$
BEGIN
  UPDATE color_catalog 
  SET usage_count = usage_count - 1 
  WHERE hex_code = OLD.hex_code;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Update on change (color changed in a palette)
CREATE OR REPLACE FUNCTION update_color_usage_on_change() RETURNS TRIGGER AS $$
BEGIN
  IF OLD.hex_code IS DISTINCT FROM NEW.hex_code THEN
    UPDATE color_catalog SET usage_count = usage_count - 1 WHERE hex_code = OLD.hex_code;
    UPDATE color_catalog SET usage_count = usage_count + 1 WHERE hex_code = NEW.hex_code;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================
-- TRIGGERS: attach functions to palette_colors events
-- ============================================
CREATE TRIGGER trg_increment_color_usage
AFTER INSERT ON palette_colors
FOR EACH ROW EXECUTE FUNCTION increment_color_usage();

CREATE TRIGGER trg_decrement_color_usage
AFTER DELETE ON palette_colors
FOR EACH ROW EXECUTE FUNCTION decrement_color_usage();

CREATE TRIGGER trg_update_color_usage
AFTER UPDATE ON palette_colors
FOR EACH ROW EXECUTE FUNCTION update_color_usage_on_change();

-- ============================================
-- RECOMMENDED INDEXES
-- ============================================
CREATE INDEX idx_palettes_user_id ON palettes(user_id);
CREATE INDEX idx_palettes_is_public ON palettes(is_public);
CREATE INDEX idx_palette_colors_palette_id ON palette_colors(palette_id);
CREATE INDEX idx_palette_colors_hex_code ON palette_colors(hex_code);
CREATE INDEX idx_color_catalog_hue ON color_catalog(hue);
CREATE INDEX idx_color_catalog_lightness ON color_catalog(lightness);
CREATE INDEX idx_color_catalog_usage_count ON color_catalog(usage_count DESC);
