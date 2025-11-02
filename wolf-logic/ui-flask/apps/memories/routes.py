# -*- encoding: utf-8 -*-
"""
Memory Management Routes
"""

from apps.memories import blueprint
from flask import render_template, request, jsonify, flash, redirect, url_for, send_file
from apps.memories.api_client import MemoryAPIClient
from datetime import datetime
import io

api_client = MemoryAPIClient()

# ========== Dashboard ==========

@blueprint.route('/')
def dashboard():
    """Main dashboard with stats and recent memories"""
    try:
        # Get stats
        stats = api_client.get_stats()

        # Get recent memories (first page)
        memories_data = api_client.list_memories(page=1, page_size=10, sort_by="created_at", sort_order="desc")

        # Get all apps for filter
        apps_data = api_client.list_apps(page_size=100)

        # Get all categories
        categories = api_client.get_categories()

        return render_template(
            'memories/dashboard.html',
            stats=stats,
            memories=memories_data.get('memories', []),
            total=memories_data.get('total', 0),
            apps=apps_data.get('apps', []),
            categories=categories,
            segment='dashboard'
        )
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('memories/dashboard.html', stats={}, memories=[], apps=[], categories=[])

# ========== Memories List ==========

@blueprint.route('/memories')
def memories():
    """List all memories with filtering"""
    try:
        # Get filter parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')
        apps_filter = request.args.getlist('apps')
        categories_filter = request.args.getlist('categories')
        show_archived = request.args.get('show_archived', 'false').lower() == 'true'
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # Get memories
        data = api_client.list_memories(
            page=page,
            page_size=page_size,
            search=search,
            apps=apps_filter,
            categories=categories_filter,
            show_archived=show_archived,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Get filter options
        apps_data = api_client.list_apps(page_size=100)
        categories = api_client.get_categories()

        return render_template(
            'memories/list.html',
            memories=data.get('memories', []),
            total=data.get('total', 0),
            page=page,
            page_size=page_size,
            total_pages=data.get('total_pages', 0),
            apps=apps_data.get('apps', []),
            categories=categories,
            filters={
                'search': search,
                'apps': apps_filter,
                'categories': categories_filter,
                'show_archived': show_archived,
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            segment='memories'
        )
    except Exception as e:
        flash(f'Error loading memories: {str(e)}', 'danger')
        return render_template('memories/list.html', memories=[], apps=[], categories=[])

# ========== Memory Detail ==========

@blueprint.route('/memories/<memory_id>')
def memory_detail(memory_id):
    """View single memory with details"""
    try:
        memory = api_client.get_memory(memory_id)
        access_log = api_client.get_access_log(memory_id)
        related = api_client.get_related_memories(memory_id)

        return render_template(
            'memories/detail.html',
            memory=memory,
            access_log=access_log.get('logs', []),
            related_memories=related.get('memories', []),
            segment='memories'
        )
    except Exception as e:
        flash(f'Error loading memory: {str(e)}', 'danger')
        return redirect(url_for('memories_blueprint.memories'))

# ========== Create Memory ==========

@blueprint.route('/memories/create', methods=['GET', 'POST'])
def create_memory():
    """Create new memory"""
    if request.method == 'POST':
        try:
            text = request.form.get('text', '').strip()
            app_name = request.form.get('app_name', 'wolf-logic-ui')

            if not text:
                flash('Memory text is required', 'warning')
                return redirect(url_for('memories_blueprint.create_memory'))

            result = api_client.create_memory(text=text, app_name=app_name)
            flash('Memory created successfully!', 'success')
            return redirect(url_for('memories_blueprint.memory_detail', memory_id=result.get('id')))
        except Exception as e:
            flash(f'Error creating memory: {str(e)}', 'danger')
            return redirect(url_for('memories_blueprint.create_memory'))

    return render_template('memories/create.html', segment='memories')

# ========== Update Memory ==========

@blueprint.route('/memories/<memory_id>/edit', methods=['GET', 'POST'])
def edit_memory(memory_id):
    """Edit memory content"""
    if request.method == 'POST':
        try:
            content = request.form.get('content', '').strip()

            if not content:
                flash('Memory content is required', 'warning')
                return redirect(url_for('memories_blueprint.edit_memory', memory_id=memory_id))

            api_client.update_memory(memory_id, content)
            flash('Memory updated successfully!', 'success')
            return redirect(url_for('memories_blueprint.memory_detail', memory_id=memory_id))
        except Exception as e:
            flash(f'Error updating memory: {str(e)}', 'danger')

    try:
        memory = api_client.get_memory(memory_id)
        return render_template('memories/edit.html', memory=memory, segment='memories')
    except Exception as e:
        flash(f'Error loading memory: {str(e)}', 'danger')
        return redirect(url_for('memories_blueprint.memories'))

# ========== Delete Memory ==========

@blueprint.route('/memories/<memory_id>/delete', methods=['POST'])
def delete_memory(memory_id):
    """Delete memory"""
    try:
        api_client.delete_memories([memory_id])
        flash('Memory deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting memory: {str(e)}', 'danger')

    return redirect(url_for('memories_blueprint.memories'))

# ========== Bulk Actions ==========

@blueprint.route('/memories/bulk-delete', methods=['POST'])
def bulk_delete():
    """Delete multiple memories"""
    try:
        memory_ids = request.form.getlist('memory_ids')
        if not memory_ids:
            flash('No memories selected', 'warning')
            return redirect(url_for('memories_blueprint.memories'))

        api_client.delete_memories(memory_ids)
        flash(f'{len(memory_ids)} memories deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting memories: {str(e)}', 'danger')

    return redirect(url_for('memories_blueprint.memories'))

@blueprint.route('/memories/bulk-pause', methods=['POST'])
def bulk_pause():
    """Pause/unpause multiple memories"""
    try:
        memory_ids = request.form.getlist('memory_ids')
        is_paused = request.form.get('is_paused', 'true').lower() == 'true'

        if not memory_ids:
            flash('No memories selected', 'warning')
            return redirect(url_for('memories_blueprint.memories'))

        api_client.pause_memories(memory_ids=memory_ids, is_paused=is_paused)
        action = 'paused' if is_paused else 'resumed'
        flash(f'{len(memory_ids)} memories {action} successfully!', 'success')
    except Exception as e:
        flash(f'Error pausing/resuming memories: {str(e)}', 'danger')

    return redirect(url_for('memories_blueprint.memories'))

@blueprint.route('/memories/bulk-archive', methods=['POST'])
def bulk_archive():
    """Archive multiple memories"""
    try:
        memory_ids = request.form.getlist('memory_ids')

        if not memory_ids:
            flash('No memories selected', 'warning')
            return redirect(url_for('memories_blueprint.memories'))

        api_client.archive_memories(memory_ids)
        flash(f'{len(memory_ids)} memories archived successfully!', 'success')
    except Exception as e:
        flash(f'Error archiving memories: {str(e)}', 'danger')

    return redirect(url_for('memories_blueprint.memories'))

# ========== Apps Management ==========

@blueprint.route('/apps')
def apps():
    """List all apps"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')

        data = api_client.list_apps(search=search, page=page, page_size=page_size)

        return render_template(
            'memories/apps.html',
            apps=data.get('apps', []),
            total=data.get('total', 0),
            page=page,
            page_size=page_size,
            total_pages=data.get('total_pages', 0),
            segment='apps'
        )
    except Exception as e:
        flash(f'Error loading apps: {str(e)}', 'danger')
        return render_template('memories/apps.html', apps=[])

@blueprint.route('/apps/<app_id>')
def app_detail(app_id):
    """View app details"""
    try:
        app = api_client.get_app(app_id)
        memories_data = api_client.get_app_memories(app_id, page=1, page_size=20)

        return render_template(
            'memories/app_detail.html',
            app=app,
            memories=memories_data.get('memories', []),
            segment='apps'
        )
    except Exception as e:
        flash(f'Error loading app: {str(e)}', 'danger')
        return redirect(url_for('memories_blueprint.apps'))

@blueprint.route('/apps/<app_id>/toggle', methods=['POST'])
def toggle_app(app_id):
    """Toggle app active status"""
    try:
        is_active = request.form.get('is_active', 'false').lower() == 'true'
        api_client.update_app_status(app_id, is_active)
        status = 'activated' if is_active else 'deactivated'
        flash(f'App {status} successfully!', 'success')
    except Exception as e:
        flash(f'Error updating app: {str(e)}', 'danger')

    return redirect(url_for('memories_blueprint.app_detail', app_id=app_id))

# ========== Settings/Config ==========

@blueprint.route('/settings', methods=['GET', 'POST'])
def settings():
    """View and update configuration"""
    if request.method == 'POST':
        try:
            # Get form data and update config
            config_data = {
                'llm_provider': request.form.get('llm_provider'),
                'llm_model': request.form.get('llm_model'),
                'embedder_provider': request.form.get('embedder_provider'),
                'embedder_model': request.form.get('embedder_model'),
                'custom_instructions': request.form.get('custom_instructions', '')
            }

            api_client.update_config(config_data)
            flash('Configuration updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating configuration: {str(e)}', 'danger')

    try:
        config = api_client.get_config()
        return render_template('memories/settings.html', config=config, segment='settings')
    except Exception as e:
        flash(f'Error loading configuration: {str(e)}', 'danger')
        return render_template('memories/settings.html', config={})

# ========== Backup/Export ==========

@blueprint.route('/export')
def export_memories():
    """Export all memories as zip"""
    try:
        zip_data = api_client.export_memories()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'memories_backup_{timestamp}.zip'

        return send_file(
            io.BytesIO(zip_data),
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error exporting memories: {str(e)}', 'danger')
        return redirect(url_for('memories_blueprint.dashboard'))

# ========== API Endpoints for AJAX ==========

@blueprint.route('/api/memories/search')
def api_search_memories():
    """AJAX endpoint for memory search"""
    try:
        search = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        data = api_client.list_memories(
            page=page,
            page_size=page_size,
            search=search
        )

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blueprint.route('/api/categories')
def api_categories():
    """AJAX endpoint for categories"""
    try:
        categories = api_client.get_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blueprint.route('/api/stats')
def api_stats():
    """AJAX endpoint for stats"""
    try:
        stats = api_client.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
