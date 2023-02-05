! Description:
! Main program.
program fs_solver
    use data_model
    use input_output
    implicit none
    
    integer                     :: argc    ! command line arguments count
    character(256), allocatable :: argv(:) ! command line arguments vector
    character(8)                :: date    ! current date
    character(10)               :: time    ! current time
    type(t_mdb)                 :: mdb     ! model database
    integer                     :: i       ! loop counter
    
    ! get command line arguments
    argc = command_argument_count() + 1
    allocate(argv(argc))
    do i = 1, argc
        call get_command_argument(i - 1, argv(i))
    end do
    
    ! print info
    call date_and_time(date, time)
    print '("Solver has started")'
    print '(A,"-",A,"-",A," ",A,":",A,":",A)', date(1:4), date(5:6), date(7:8), time(1:2), time(3:4), time(5:6)
    print '("")'
    
    ! read solver job input
    print '("Loading solver job input from file: ''",A,"''")', trim(argv(1))
    mdb = read_input(trim(argv(1)))
    print '("Solver job input loaded")'
    print '("")'
    
    ! compute algebraic connectivity
    print '("Building algebraic connectivity")'
    call mdb%build_dofs()
    print '("Active degrees of freedom: ",I0)', mdb%n_adofs
    print '("Inactive degrees of freedom: ",I0)', mdb%n_idofs
    print '("")'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    if (allocated(argv)) deallocate(argv)
    
    

    
end program


!!!program test
!!!    use data_model
!!!    use input_output
!!!    use execution_model
!!!    use linear_algebra
!!!    implicit none
!!!    
!!!    type(t_mdb)      :: mdb
!!!    type(t_element)  :: element
!!!    type(t_section)  :: section
!!!    type(t_material) :: material
!!!
!!!    type(t_sparse) :: Kaa, Kab
!!!    type(t_matrix), allocatable :: Ks(:)
!!!    integer :: i, j, il, ig, jl, jg
!!!    
!!!    real :: load(50), x(50)
!!!    
!!!    
!!!    integer :: pt(64), maxfct, mnum, mtype, phase, n, nrhs, iparm(64), msglvl, error
!!!    integer, allocatable :: perm(:)
!!!    real lol
!!!    
!!!    mdb = read_input('C:/Users/Carlos/Desktop/data.txt')
!!!    

!!!    
!!!    
!!!
!!!    load(2*(5- 1) + 1) = 5.0
!!!    load(2*(10- 1) + 1) = 5.0
!!!    load(2*(15- 1) + 1) = 5.0
!!!    load(2*(20 - 1) + 1) = 5.0
!!!    load(2*(25 - 1) + 1) = 5.0
!!!    
!!!    
!!!    
!!!    pt(:) = 0
!!!    maxfct = 1
!!!    mnum = 1
!!!    mtype = 11
!!!    phase = 13
!!!    n = Kaa%n_rows
!!!    nrhs = 1
!!!    msglvl = 0
!!!    allocate(perm(n))
!!!    
!!!    do i = 1, 100000
!!!    call pardiso (pt, maxfct, mnum, mtype, phase, n, Kaa%val, Kaa%row, Kaa%col, perm, nrhs, iparm, msglvl, load, x, error)
!!!    end do
!!!    
!!!    deallocate(perm)
!!!    
!!!    
!!!    
!!!    lol = maxval(x)
!!!    
!!!    
!!!
!!!    
!!!!internal static SparseDOK GetGlobalStiffnessMatrix(ModelDatabase model)
!!!!{
!!!!	Matrix[] Kes = new Matrix[model.Mesh.Elements.Count];
!!!!	Parallel.For(0, Kes.Length, i => Kes[i] = model.Mesh.Elements[i].GetStiffnessMatrix());
!!!!
!!!!	SparseDOK K = new(model.DegreesOfFreedom, model.DegreesOfFreedom);
!!!!	for (int i = 0; i < Kes.Length; i++) LocalToGlobal_Matrix(K, Kes[i], model.Mesh.Elements[i]);
!!!!	return K;
!!!!}
!!!    
!!!
!!!
!!!    print *, 'Hi'
!!!
!!!    end program
!!!
!!!        !Ub = zeros(size(Kab, 2), 1);
!!!        !for bc = model.boundaryConditions
!!!        !    nodeSet = getField(model.mesh.nodeSets, bc.nodeSetName);
!!!        !    nodeIndices = nodeSet.indices;
!!!        !    for il = 1 : length(nodeIndices)
!!!        !        ig = nodeIndices(il);
!!!        !        for jjj = 1 : length(bc.activeDOFs)
!!!        !            dim = bc.activeDOFs(jjj);
!!!        !            ind = dofTable(dim, ig);
!!!        !            Ub(-ind) = bc.values(jjj);
!!!        !        end
!!!        !    end
!!!        !end
!!!    !Pg = Pg - Kab*Ub;