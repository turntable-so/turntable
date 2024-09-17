import React, { useEffect, useState } from 'react';
import { getAssets } from '@/app/actions/actions';
import DataTable from '@/components/ui/data-table';

const ViewerContainer: React.FC = () => {
    return (
        <div className="p-8">
            <DataTable />
            <div className='h-12' />
        </div>
    );
};

export default ViewerContainer;