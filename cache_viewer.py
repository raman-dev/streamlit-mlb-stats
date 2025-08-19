import streamlit as st
import diskcache
import pandas as pd
import json
from datetime import datetime
import server

st.title("📊 Cache Viewer")
st.markdown("View and analyze the contents of the diskcache database")

def get_cache_stats():
    """Get basic statistics about the cache"""
    with diskcache.Cache(server.CACHE_DIR) as cache:
        total_keys = len(cache)
        cache_size = cache.volume()
        
        # Categorize keys by type
        key_types = {}
        for key in cache.iterkeys():
            key_type = key.split('_')[0] if '_' in key else 'other'
            key_types[key_type] = key_types.get(key_type, 0) + 1
        
        return {
            'total_keys': total_keys,
            'cache_size_mb': cache_size / (1024 * 1024),
            'key_types': key_types
        }

def display_cache_overview():
    """Display cache overview statistics"""
    st.subheader("🔍 Cache Overview")
    
    try:
        stats = get_cache_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Keys", stats['total_keys'])
        with col2:
            st.metric("Cache Size", f"{stats['cache_size_mb']:.2f} MB")
        with col3:
            st.metric("Key Types", len(stats['key_types']))
        
        # Display key type breakdown
        st.subheader("📈 Key Type Distribution")
        if stats['key_types']:
            df_types = pd.DataFrame(list(stats['key_types'].items()), 
                                  columns=['Key Type', 'Count'])
            df_types = df_types.sort_values('Count', ascending=False)
            st.bar_chart(df_types.set_index('Key Type'))
        
    except Exception as e:
        st.error(f"Error accessing cache: {str(e)}")

def get_cache_keys_by_type():
    """Get all cache keys organized by type"""
    with diskcache.Cache(server.CACHE_DIR) as cache:
        keys_by_type = {}
        for key in cache.iterkeys():
            key_type = key.split('_')[0] if '_' in key else 'other'
            if key_type not in keys_by_type:
                keys_by_type[key_type] = []
            keys_by_type[key_type].append(key)
        
        # Sort keys within each type
        for key_type in keys_by_type:
            keys_by_type[key_type].sort()
        
        return keys_by_type

def display_games_played_cache():
    """Display games played cache data as tables"""
    st.subheader("🎮 Games Played Cache")
    
    try:
        with diskcache.Cache(server.CACHE_DIR) as cache:
            games_played_keys = [key for key in cache.iterkeys() if key.startswith('games_played_')]
            
            if not games_played_keys:
                st.info("No games played data found in cache")
                return
            
            selected_key = st.selectbox("Select Games Played Cache Entry", games_played_keys)
            
            if selected_key:
                data = cache.get(selected_key)
                if data and 'data' in data:
                    st.write(f"**Cache Key:** `{selected_key}`")
                    st.write(f"**End Date:** {data.get('endDate', 'N/A')}")
                    st.write(f"**Total Games:** {len(data['data'])}")
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(data['data'])
                    if not df.empty:
                        # Select relevant columns for display
                        display_columns = ['game_date', 'home_name', 'away_name', 'home_score', 
                                         'away_score', 'status', 'game_id']
                        available_columns = [col for col in display_columns if col in df.columns]
                        
                        if available_columns:
                            st.dataframe(df[available_columns], use_container_width=True)
                        else:
                            st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("No game data available")
                else:
                    st.error("Invalid cache data format")
    
    except Exception as e:
        st.error(f"Error displaying games played cache: {str(e)}")

def display_linescore_cache():
    """Display linescore cache data"""
    st.subheader("📊 Linescore Cache")
    
    try:
        with diskcache.Cache(server.CACHE_DIR) as cache:
            linescore_keys = [key for key in cache.iterkeys() if key.startswith('linescore_')]
            
            if not linescore_keys:
                st.info("No linescore data found in cache")
                return
            
            # Show summary
            st.write(f"**Total Linescores Cached:** {len(linescore_keys)}")
            
            # Sample a few for display
            sample_size = min(10, len(linescore_keys))
            sample_keys = linescore_keys[:sample_size]
            
            selected_key = st.selectbox("Select Linescore to View", sample_keys)
            
            if selected_key:
                linescore_data = cache.get(selected_key)
                if linescore_data:
                    st.write(f"**Cache Key:** `{selected_key}`")
                    
                    # Display as JSON in expandable section
                    with st.expander("Raw Linescore Data"):
                        st.json(linescore_data)
                    
                    # Try to extract key information
                    if 'teams' in linescore_data:
                        teams_data = []
                        for side in ['home', 'away']:
                            if side in linescore_data['teams']:
                                team_data = linescore_data['teams'][side]
                                teams_data.append({
                                    'Side': side.title(),
                                    'Runs': team_data.get('runs', 'N/A'),
                                    'Hits': team_data.get('hits', 'N/A'),
                                    'Errors': team_data.get('errors', 'N/A')
                                })
                        
                        if teams_data:
                            st.subheader("Team Stats")
                            df_teams = pd.DataFrame(teams_data)
                            st.table(df_teams)
    
    except Exception as e:
        st.error(f"Error displaying linescore cache: {str(e)}")

def display_team_game_containers():
    """Display team game container data"""
    st.subheader("🏟️ Team Game Containers")
    
    try:
        with diskcache.Cache(server.CACHE_DIR) as cache:
            tgc_keys = [key for key in cache.iterkeys() if 'team_game_container' in key]
            
            if not tgc_keys:
                st.info("No team game container data found in cache")
                return
            
            selected_key = st.selectbox("Select Team Game Container", tgc_keys)
            
            if selected_key:
                tgc_data = cache.get(selected_key)
                if tgc_data:
                    st.write(f"**Cache Key:** `{selected_key}`")
                    st.write(f"**Team ID:** {getattr(tgc_data, 'teamId', 'N/A')}")
                    st.write(f"**Season:** {getattr(tgc_data, 'season', 'N/A')}")
                    
                    if hasattr(tgc_data, 'playedGameIds'):
                        st.write(f"**Total Games:** {len(tgc_data.playedGameIds)}")
                        
                        # Display game IDs as a table
                        if tgc_data.playedGameIds:
                            df_games = pd.DataFrame({
                                'Game ID': tgc_data.playedGameIds
                            })
                            st.dataframe(df_games, use_container_width=True)
                    
                    # Show additional fields for TeamGameContainer2
                    if hasattr(tgc_data, 'mostRecentDate'):
                        st.write(f"**Most Recent Date:** {getattr(tgc_data, 'mostRecentDate', 'N/A')}")
                        st.write(f"**Most Recent Game ID:** {getattr(tgc_data, 'mostRecentGameId', 'N/A')}")
    
    except Exception as e:
        st.error(f"Error displaying team game containers: {str(e)}")

def display_cache_management():
    """Display cache management tools"""
    st.subheader("🛠️ Cache Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Cache Stats", type="secondary"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All Cache", type="secondary"):
            if st.session_state.get('confirm_clear_cache', False):
                try:
                    with diskcache.Cache(server.CACHE_DIR) as cache:
                        cache.clear()
                    st.success("Cache cleared successfully!")
                    st.session_state['confirm_clear_cache'] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing cache: {str(e)}")
            else:
                st.session_state['confirm_clear_cache'] = True
                st.warning("⚠️ Click again to confirm cache clearing")

# Main page layout
display_cache_overview()

st.divider()

# Tabs for different cache types
tab1, tab2, tab3, tab4 = st.tabs(["🎮 Games Played", "📊 Linescores", "🏟️ Team Containers", "🛠️ Management"])

with tab1:
    display_games_played_cache()

with tab2:
    display_linescore_cache()

with tab3:
    display_team_game_containers()

with tab4:
    display_cache_management()

# Add a section to show all cache keys for debugging
with st.expander("🔍 All Cache Keys (Debug)"):
    try:
        keys_by_type = get_cache_keys_by_type()
        for key_type, keys in keys_by_type.items():
            st.write(f"**{key_type.title()}** ({len(keys)} keys):")
            for key in keys:
                st.code(key)
    except Exception as e:
        st.error(f"Error displaying cache keys: {str(e)}")
