from flask import Flask, request, render_template, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# Long-lived access token stored in the app
ACCESS_TOKEN = 'EAAOikNxgJ0IBOwTQvirA5BrXf3lGIDR8USPNvL98dONweCojImBULraQ3ENY1vpRooK85AU81aKJPhP59HxSBP3OtkIXYTmD1vHkDf05afAU267sLcw5NjayLqja7ZBQYXYKSdbk3OjArxFeqZBFZBjHZAdK01eAmAr8ExteEGsVZA67JjKLSQlZAmE8V5tOK9ogZDZD'  # Replace with your actual token

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_viral_posts', methods=['POST'])
def get_viral_posts():
    try:
        # Get multiple page IDs from input
        page_ids = request.form.get('page_ids').split(',')
        date = request.form.get('date')
        like_threshold = int(request.form.get('like_threshold', 1000))

        # Validate input
        if not page_ids or not date:
            return jsonify({'status': 'error', 'message': 'Missing page IDs or date'}), 400

        # Convert date to ISO format (e.g., 2025-05-01T00:00:00)
        date_from = f"{date}T00:00:00"
        date_to = f"{date}T23:59:59"

        viral_posts = []

        # Iterate over each page ID
        for page_id in page_ids:
            page_id = page_id.strip()

            # Fetch posts from the page
            url = f'https://graph.facebook.com/v17.0/{page_id}/posts'
            params = {
                'access_token': ACCESS_TOKEN,
                'fields': 'id,message,permalink_url,likes.summary(true)',
                'since': date_from,
                'until': date_to
            }

            response = requests.get(url, params=params)
            data = response.json()

            # Check for errors from Facebook API
            if 'error' in data:
                return jsonify({'status': 'error', 'message': data['error']['message']}), 500

            # Process each post
            for post in data.get('data', []):
                post_id = post['id']
                like_count = post.get('likes', {}).get('summary', {}).get('total_count', 0)

                if like_count >= like_threshold:
                    viral_posts.append({
                        'page_id': page_id,
                        'message': post.get('message', 'No text content'),
                        'permalink_url': post['permalink_url'],
                        'like_count': like_count
                    })

        # If no viral posts are found
        if not viral_posts:
            return jsonify({'status': 'success', 'message': 'No viral posts found', 'viral_posts': []})

        return jsonify({'status': 'success', 'viral_posts': viral_posts})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    